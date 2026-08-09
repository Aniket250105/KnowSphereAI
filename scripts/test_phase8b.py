import os
import json
import asyncio
from src.evaluation.datasets import EvaluationDataset
from src.evaluation.metrics import EvaluationMetrics
from src.database.models import EvaluationRunModel, EvaluationResultModel, PromptExperimentModel
from src.database.database import get_db

def test_dataset_loading():
    print("Testing dataset loading...")
    
    # Create dummy JSON dataset
    dummy_json = [
        {
            "query": "Test query", 
            "expected_answer": "Test Answer", 
            "expected_sources": ["doc1.txt"],
            "difficulty": "easy",
            "category": "test"
        }
    ]
    with open("test_dummy.json", "w") as f:
        json.dump(dummy_json, f)
        
    ds = EvaluationDataset("test_dummy.json", version="1.0")
    queries = ds.get_queries("Quick")
    assert len(queries) == 1
    assert queries[0]["query"] == "Test query"
    assert queries[0]["dataset_version"] == "1.0"
    
    os.remove("test_dummy.json")
    print("Dataset loading passed.")

def test_metrics():
    print("Testing metric calculations...")
    metrics = EvaluationMetrics()
    
    # Recall
    recall = metrics.calculate_recall_at_k(["doc1.txt", "doc2.txt"], ["doc2.txt"], k=5)
    assert recall == 1.0
    
    # MRR
    mrr = metrics.calculate_mrr(["doc1.txt", "doc2.txt"], ["doc2.txt"])
    assert mrr == 0.5
    
    # Overall Score
    overall = metrics.calculate_overall_score(mrr=1.0, grounding=1.0, citation=1.0, latency_seconds=1.0)
    # Weights: 0.4 + 0.3 + 0.2 + (0.9 * 0.1) = 0.9 + 0.09 = 0.99
    assert abs(overall - 0.99) < 0.001
    
    print("Metrics calculations passed.")

def test_models():
    print("Testing database model instantiation...")
    run = EvaluationRunModel(
        id="run_123",
        dataset_name="test_data",
        average_score=0.95
    )
    assert run.id == "run_123"
    
    res = EvaluationResultModel(
        run_id="run_123",
        query="q1",
        grounding_score=0.8
    )
    assert res.run_id == "run_123"
    
    print("Database model instantiation passed.")

if __name__ == "__main__":
    test_dataset_loading()
    test_metrics()
    test_models()
    print("All Phase 8B tests completed successfully!")
