import os
import threading
from typing import List, Dict, Any, Tuple
from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.core import config
from src.core.logger import get_logger
from src.models.vector_point import VectorPoint
from src.vectorstore.base_vectorstore import BaseVectorStore

logger = get_logger(__name__)

class QdrantVectorStore(BaseVectorStore):
    """
    Qdrant implementation of the BaseVectorStore interface.
    Uses Singleton pattern to prevent file locking issues with local Qdrant.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(QdrantVectorStore, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
        
    def delete(self, filters: Dict[str, Any]) -> bool:
        """
        Deletes vectors matching the specified payload filters.
        """
        must_conditions = []
        for key, value in filters.items():
            must_conditions.append(models.FieldCondition(
                key=key,
                match=models.MatchValue(value=value)
            ))
            
        filter_query = models.Filter(must=must_conditions)
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(filter=filter_query)
            )
            logger.info(f"Deleted vectors matching filter: {filters} from collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
            
        self.collection_name = config.QDRANT_COLLECTION
        db_path = config.VECTOR_DB_PATH
        
        qdrant_url = getattr(config, 'QDRANT_URL', None)
        qdrant_api_key = getattr(config, 'QDRANT_API_KEY', None)
        qdrant_timeout = getattr(config, 'QDRANT_TIMEOUT', 10)
        
        if qdrant_url:
            logger.info(f"Connecting to remote Qdrant at {qdrant_url}")
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                timeout=qdrant_timeout
            )
        else:
            # Ensure path exists for local mode
            os.makedirs(db_path, exist_ok=True)
            logger.info(f"Connecting to local Qdrant at {db_path}")
            self.client = QdrantClient(path=str(db_path), timeout=qdrant_timeout)
            
        self._initialized = True
        
    def upsert(self, points: List[VectorPoint]):
        """Inserts or updates vector points in the collection."""
        if not points:
            return
            
        qdrant_points = [
            models.PointStruct(
                id=point.id, 
                vector=point.vector, 
                payload=point.payload
            )
            for point in points
        ]
        
        logger.info(f"Uploading {len(qdrant_points)} vectors to collection '{self.collection_name}'...")
        self.client.upsert(
            collection_name=self.collection_name,
            points=qdrant_points
        )
        
    def search(self, query_vector: List[float], top_k: int = 5, score_threshold: float = None, filters: Dict[str, Any] = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the vector store for the closest vectors.
        """
        query_filter = None
        if filters:
            must_conditions = []
            for key, val in filters.items():
                must_conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=val)
                    )
                )
            query_filter = models.Filter(must=must_conditions)

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter
        )
        
        return [(hit.payload, hit.score) for hit in response.points]
