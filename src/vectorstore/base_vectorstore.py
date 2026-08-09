from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from src.models.vector_point import VectorPoint

class BaseVectorStore(ABC):
    """
    Abstract interface for vector database CRUD operations.
    """
    
    @abstractmethod
    def upsert(self, points: List[VectorPoint]):
        """Inserts or updates vector points in the collection."""
        pass
        
    @abstractmethod
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorPoint]:
        """
        Perform a semantic similarity search to find top-k matches.
        """
        pass
        
    @abstractmethod
    def delete(self, filters: Dict[str, Any]) -> bool:
        """
        Deletes vectors matching the specified payload filters.
        """
        pass
