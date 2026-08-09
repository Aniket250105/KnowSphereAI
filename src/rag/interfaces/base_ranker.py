from abc import ABC, abstractmethod
from src.models.search_result import SearchResponse

class BaseContextRanker(ABC):
    @abstractmethod
    def rank(self, search_response: SearchResponse) -> SearchResponse:
        """Ranks retrieved chunks based on secondary heuristics like BM25 and chunk position."""
        pass
