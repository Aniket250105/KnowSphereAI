from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
import os

from src.auth.permissions import require_role
from src.evaluation.benchmark_runner import BenchmarkRunner
from src.evaluation.datasets import EvaluationDataset
from src.evaluation.retrieval_testing import RetrievalStrategyTester
from src.api.dependencies import get_db_repository, get_rag_pipeline

evaluation_router = APIRouter()

@evaluation_router.post("/run")
async def run_benchmark(
    profile: str = "Quick", 
    dataset_file: str = "tests/evaluation/phase8_questions.json",
    current_user = Depends(require_role("ADMIN")),
    db_repo = Depends(get_db_repository),
    rag_pipeline = Depends(get_rag_pipeline)
):
    try:
        # Resolve full path safely for demo
        base_path = os.getcwd()
        full_path = os.path.join(base_path, dataset_file)
        
        dataset = EvaluationDataset(filepath=full_path)
        runner = BenchmarkRunner(rag_service=rag_pipeline, db_repo=db_repo)
        
        summary = await runner.run_benchmark(dataset, profile=profile)
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@evaluation_router.get("/leaderboard/retrieval")
async def get_retrieval_leaderboard(
    dataset_file: str = "tests/evaluation/phase8_questions.json",
    current_user = Depends(require_role("ADMIN")),
    db_repo = Depends(get_db_repository),
    rag_pipeline = Depends(get_rag_pipeline)
):
    try:
        base_path = os.getcwd()
        full_path = os.path.join(base_path, dataset_file)
        
        dataset = EvaluationDataset(filepath=full_path)
        runner = BenchmarkRunner(rag_service=rag_pipeline, db_repo=db_repo)
        tester = RetrievalStrategyTester(runner=runner)
        
        leaderboard = await tester.run_leaderboard(dataset)
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
