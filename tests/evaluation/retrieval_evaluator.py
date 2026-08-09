import sys
import json
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.vectorstore.qdrant_store import QdrantVectorStore
from src.embeddings.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService
from src.core.logger import get_logger

logger = get_logger(__name__)

def evaluate():
    test_cases_path = Path(__file__).parent / "retrieval_test_cases.json"
    report_path = Path(__file__).parent / "evaluation_report.json"
    failures_path = Path(__file__).parent / "failed_queries.json"
    
    with open(test_cases_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)
        
    vector_store = QdrantVectorStore()
    embedding_service = EmbeddingService()
    retrieval_service = RetrievalService(vector_store, embedding_service)
    
    total_queries = len(test_cases)
    top_1_hits = 0
    top_3_hits = 0
    total_similarity = 0.0
    total_latency = 0.0
    mrr_sum = 0.0
    
    failed_queries = []
    
    for case in test_cases:
        query = case["query"]
        expected_docs = case["expected_documents"]
        expected_keywords = [k.lower() for k in case["expected_keywords"]]
        
        response = retrieval_service.retrieve(query, top_k=3)
        total_latency += response.search_time_seconds
        
        if not response.results:
            failed_queries.append({
                "query": query,
                "expected": expected_docs,
                "retrieved": None,
                "score": 0.0
            })
            continue
            
        top_result = response.results[0]
        total_similarity += top_result.score
        
        # Validation checks
        def is_hit(result):
            if result.document_name in expected_docs:
                return True
            text_lower = result.text.lower()
            if any(k in text_lower for k in expected_keywords):
                return True
            return False
            
        # Top-1 Check
        if is_hit(top_result):
            top_1_hits += 1
            mrr_sum += 1.0
        else:
            # Check Top-3 for Recall@3 and MRR
            hit_rank = -1
            for rank, result in enumerate(response.results):
                if is_hit(result):
                    hit_rank = rank + 1
                    break
            
            if hit_rank > 0:
                top_3_hits += 1
                mrr_sum += (1.0 / hit_rank)
            else:
                failed_queries.append({
                    "query": query,
                    "expected": expected_docs,
                    "retrieved": [r.document_name for r in response.results],
                    "score": top_result.score
                })
                
        # If it wasn't top 1 but was in top 3, we already added it to top_3_hits.
        # But wait, Top-3 accuracy includes Top-1 hits.
        if is_hit(top_result):
            top_3_hits += 1 # because if it's in top 1, it's in top 3
            
    top_1_accuracy = top_1_hits / total_queries if total_queries else 0
    top_3_accuracy = top_3_hits / total_queries if total_queries else 0
    avg_similarity = total_similarity / total_queries if total_queries else 0
    avg_latency = total_latency / total_queries if total_queries else 0
    mrr = mrr_sum / total_queries if total_queries else 0
    
    report = {
        "total_queries": total_queries,
        "top_1_accuracy": round(top_1_accuracy, 4),
        "top_3_accuracy": round(top_3_accuracy, 4),
        "mrr": round(mrr, 4),
        "recall_at_3": round(top_3_accuracy, 4),
        "average_similarity_score": round(avg_similarity, 4),
        "average_retrieval_time": round(avg_latency, 4)
    }
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    with open(failures_path, "w", encoding="utf-8") as f:
        json.dump(failed_queries, f, indent=4)
        
    print("\n====================================")
    print("KNOWSPHERE RETRIEVAL EVALUATION")
    print("====================================")
    print(f"Queries Tested: {total_queries}")
    print(f"Top-1 Accuracy: {top_1_accuracy*100:.1f}%")
    print(f"Top-3 Accuracy: {top_3_accuracy*100:.1f}%")
    print(f"MRR           : {mrr:.4f}")
    print(f"Recall@3      : {top_3_accuracy*100:.1f}%")
    print(f"Avg Similarity: {avg_similarity:.4f}")
    print(f"Avg Retrieval : {avg_latency:.4f} seconds")
    print("====================================\n")

if __name__ == "__main__":
    evaluate()
