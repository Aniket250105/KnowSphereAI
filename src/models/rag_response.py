from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.models.evaluation_result import EvaluationResult

@dataclass
class RAGResponse:
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_chunks: List[Any]
    generation_time_seconds: float
    total_time_seconds: float
    confidence: str = "MEDIUM"
    suggested_questions: List[str] = field(default_factory=list)
    
    # Advanced RAG Metrics
    compressed_chunks: int = 0
    original_chunks: int = 0
    compression_ratio: float = 1.0
    retry_count: int = 0
    expanded_query: Optional[str] = None
    
    # Evaluation
    evaluation: Optional[EvaluationResult] = None

