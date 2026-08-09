from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SearchResult:
    document_id: str
    document_name: str
    chunk_id: str
    text: str
    page: int
    score: float
    metadata: Dict[str, Any]

@dataclass
class SearchResponse:
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_seconds: float
    embedding_time_seconds: float
    retrieval_time_seconds: float
