import math
from typing import List, Dict, Any

class EvaluationMetrics:
    def __init__(self, weights: Dict[str, float] = None):
        # Configurable metric weights
        self.weights = weights or {
            "retrieval": 0.4,
            "grounding": 0.3,
            "citation": 0.2,
            "latency": 0.1
        }

    # --- Retrieval Metrics ---

    @staticmethod
    def calculate_recall_at_k(retrieved_sources: List[str], expected_sources: List[str], k: int = 5) -> float:
        if not expected_sources:
            return 1.0 # If no expected sources, recall is implicitly 1.0 (nothing to recall)
        if not retrieved_sources:
            return 0.0
            
        retrieved_k = retrieved_sources[:k]
        hits = sum(1 for src in expected_sources if src in retrieved_k)
        return min(1.0, hits / len(expected_sources))

    @staticmethod
    def calculate_mrr(retrieved_sources: List[str], expected_sources: List[str]) -> float:
        if not expected_sources:
            return 1.0
        for i, src in enumerate(retrieved_sources):
            if src in expected_sources:
                return 1.0 / (i + 1)
        return 0.0

    @staticmethod
    def calculate_ndcg(retrieved_sources: List[str], expected_sources: List[str], k: int = 5) -> float:
        if not expected_sources:
            return 1.0
            
        dcg = 0.0
        for i, src in enumerate(retrieved_sources[:k]):
            if src in expected_sources:
                dcg += 1.0 / math.log2(i + 2) # i+2 because i is 0-indexed and formula needs i+1 + 1
                
        idcg = 0.0
        for i in range(min(k, len(expected_sources))):
            idcg += 1.0 / math.log2(i + 2)
            
        return dcg / idcg if idcg > 0 else 0.0

    # --- Generation Metrics ---

    @staticmethod
    def calculate_citation_accuracy(valid_count: int, warning_count: int) -> float:
        total = valid_count + warning_count
        if total == 0:
            return 1.0
        return valid_count / total

    # --- Aggregation & Scoring ---
    
    def calculate_overall_score(self, mrr: float, grounding: float, citation: float, latency_seconds: float) -> float:
        """
        Calculates a weighted overall score. Latency penalty applied if > 3 seconds.
        """
        latency_score = max(0.0, 1.0 - (latency_seconds / 10.0)) # 0 at 10 seconds
        
        score = (
            (mrr * self.weights.get("retrieval", 0.4)) +
            (grounding * self.weights.get("grounding", 0.3)) +
            (citation * self.weights.get("citation", 0.2)) +
            (latency_score * self.weights.get("latency", 0.1))
        )
        return min(1.0, score)

from pydantic import BaseModel

class RAGMetrics(BaseModel):
    query: str
    retrieval_time_seconds: float
    generation_time_seconds: float
    total_time_seconds: float
