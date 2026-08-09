from abc import ABC, abstractmethod
from src.models.search_result import SearchResponse

class BaseContextCompressor(ABC):
    @abstractmethod
    def compress(self, search_response: SearchResponse, max_length: int) -> SearchResponse:
        """Compresses the search response chunks while retaining information."""
        pass
