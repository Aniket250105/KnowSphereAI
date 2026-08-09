import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.core import config
from src.core.logger import get_logger

logger = get_logger(__name__)

class CollectionManager:
    """
    Manages the lifecycle of vector database collections.
    """
    def __init__(self, client: QdrantClient = None):
        self.collection_name = config.QDRANT_COLLECTION
        db_path = config.VECTOR_DB_PATH
        os.makedirs(db_path, exist_ok=True)
        
        # Uses provided client or instantiates a new connection
        if client:
            self.client = client
        else:
            from src.vectorstore.qdrant_store import QdrantVectorStore
            # Reuse the singleton client from QdrantVectorStore to avoid locks
            store = QdrantVectorStore()
            self.client = store.client

    def _get_distance(self):
        distance_map = {
            "cosine": models.Distance.COSINE,
            "euclid": models.Distance.EUCLID,
            "dot": models.Distance.DOT
        }
        return distance_map.get(config.VECTOR_DISTANCE.lower(), models.Distance.COSINE)

    def collection_exists(self) -> bool:
        collections = self.client.get_collections().collections
        for collection in collections:
            if collection.name == self.collection_name:
                return True
        return False

    def create_collection(self, dimension: int):
        if not self.collection_exists():
            logger.info(f"Creating Qdrant collection '{self.collection_name}'")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=dimension, 
                    distance=self._get_distance()
                )
            )
        elif config.COLLECTION_RECREATE:
            self.recreate_collection(dimension)

    def recreate_collection(self, dimension: int):
        logger.info(f"Recreating Qdrant collection '{self.collection_name}'")
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=dimension, 
                distance=self._get_distance()
            )
        )

    def delete_collection(self):
        logger.info(f"Deleting Qdrant collection '{self.collection_name}'")
        self.client.delete_collection(collection_name=self.collection_name)

    def get_vector_count(self) -> int:
        if not self.collection_exists():
            return 0
        return self.client.count(collection_name=self.collection_name).count
        
    def check_health(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
