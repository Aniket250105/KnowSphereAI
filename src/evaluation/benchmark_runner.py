import time
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.evaluation.datasets import EvaluationDataset
from src.evaluation.metrics import EvaluationMetrics
from src.evaluation.report_generator import ReportGenerator
from src.services.rag_service import RAGService
from src.database.repository import DatabaseRepository
from src.core.logger import get_logger

logger = get_logger(__name__)

class BenchmarkRunner:
    def __init__(self, rag_service: RAGService, db_repo: DatabaseRepository = None):
        self.rag_service = rag_service
        self.db_repo = db_repo
        self.metrics_engine = EvaluationMetrics()
        
    async def run_benchmark(self, dataset: EvaluationDataset, profile: str = "Standard", config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a benchmark via the RAG pipeline without modifying the pipeline itself.
        """
        run_id = f"benchmark_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        queries = dataset.get_queries(profile)
        
        logger.info(f"Starting benchmark {run_id} using {profile} profile ({len(queries)} queries)")
        
        results = []
        summary = {
            "dataset_name": os.path.basename(dataset.filepath),
            "dataset_version": dataset.get_version(),
            "total_queries": len(queries),
            "configuration": config or {},
            "start_time": datetime.now().isoformat()
        }
        
        total_mrr = 0.0
        total_recall = 0.0
        total_grounding = 0.0
        total_citation = 0.0
        total_latency = 0.0
        hallucinations = 0
        
        for item in queries:
            query_text = item["query"]
            expected_sources = item["expected_sources"]
            
            # Observe via Pipeline
            response = self.rag_service.ask(query_text)
            
            # Extract basic data
            retrieved_sources = [src.get("document") for src in response.sources]
            
            # Metrics
            recall = self.metrics_engine.calculate_recall_at_k(retrieved_sources, expected_sources, k=5)
            mrr = self.metrics_engine.calculate_mrr(retrieved_sources, expected_sources)
            
            # Generation Metrics (Extracted from EvaluationResult if available)
            eval_res = response.evaluation
            grounding_score = eval_res.grounding.score if eval_res and eval_res.grounding else 0.0
            
            citation_val = eval_res.citation_validation if eval_res else None
            if citation_val:
                citation_accuracy = self.metrics_engine.calculate_citation_accuracy(
                    len(citation_val.valid_sources), len(citation_val.warnings)
                )
            else:
                citation_accuracy = 1.0
                
            is_hallucination = False
            if eval_res and eval_res.hallucination and eval_res.hallucination.risk in ["MEDIUM", "HIGH"]:
                is_hallucination = True
                hallucinations += 1
                
            latency = response.total_time_seconds
            
            # Failure Explorer Data
            failure_reason = ""
            if recall == 0 and expected_sources:
                failure_reason = "Low recall / Wrong document retrieved"
            elif is_hallucination:
                failure_reason = "Hallucination detected"
            elif grounding_score < 0.6:
                failure_reason = "Poor grounding"
                
            result_row = {
                "query": query_text,
                "expected_answer": item.get("expected_answer", ""),
                "answer": response.answer,
                "retrieved_context": "\\n".join(response.retrieved_chunks)[:500] + "...", # truncate
                "recall": recall,
                "mrr": mrr,
                "grounding_score": grounding_score,
                "citation_score": citation_accuracy,
                "latency": latency,
                "failure_reason": failure_reason
            }
            results.append(result_row)
            
            total_recall += recall
            total_mrr += mrr
            total_grounding += grounding_score
            total_citation += citation_accuracy
            total_latency += latency
            
        # Averages
        n = len(queries) if len(queries) > 0 else 1
        summary["average_recall"] = total_recall / n
        summary["average_mrr"] = total_mrr / n
        summary["average_grounding"] = total_grounding / n
        summary["average_citation"] = total_citation / n
        summary["average_latency"] = total_latency / n
        summary["hallucination_rate"] = hallucinations / n
        
        overall_score = self.metrics_engine.calculate_overall_score(
            summary["average_mrr"],
            summary["average_grounding"],
            summary["average_citation"],
            summary["average_latency"]
        )
        summary["average_score"] = overall_score
        summary["end_time"] = datetime.now().isoformat()
        
        # Baseline Comparison
        if self.db_repo:
            baseline = await self._get_baseline()
            if baseline:
                summary["baseline_comparison"] = {
                    "average_score": overall_score - baseline.get("average_score", 0),
                    "average_latency": summary["average_latency"] - baseline.get("average_latency", 0),
                    "average_grounding": summary["average_grounding"] - baseline.get("average_grounding", 0)
                }
            
            await self._save_run(run_id, summary, results)
            
        # Report
        report_dir = ReportGenerator.generate(run_id, summary, results)
        summary["report_dir"] = report_dir
        
        return summary
        
    async def _get_baseline(self) -> Dict[str, Any]:
        if not self.db_repo: return None
        # In a real impl, fetch the last run from EvaluationRunModel
        return None
        
    async def _save_run(self, run_id: str, summary: Dict[str, Any], results: List[Dict[str, Any]]):
        if not self.db_repo: return
        # Persistence logic would go here.
        # It relies on the new DB models added in Phase 8B.
        pass

import os
