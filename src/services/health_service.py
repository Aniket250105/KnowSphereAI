from src.core.logger import get_logger
from src.models.health_status import HealthStatus
from src.vectorstore.local_store import LocalVectorStore
from src.embeddings.embedding_model import EmbeddingModel

logger = get_logger(__name__)

class HealthService:
    def __init__(self):
        self.vector_store = LocalVectorStore()
        self.embedding_model = EmbeddingModel()
        
    def check_embedding_model(self) -> HealthStatus:
        try:
            dim = self.embedding_model.get_dimension()
            return HealthStatus(status="healthy", details={"dimension": dim})
        except Exception as e:
            logger.error(f"Embedding model health check failed: {e}")
            return HealthStatus(status="unhealthy", details={"error": str(e)})

    def check_vector_database(self) -> HealthStatus:
        try:
            if self.vector_store:
                return HealthStatus(status="healthy", details={"connection": "ok", "vectors": len(self.vector_store.points)})
            return HealthStatus(status="unhealthy", details={"connection": "failed"})
        except Exception as e:
            logger.error(f"Vector database health check failed: {e}")
            return HealthStatus(status="unhealthy", details={"error": str(e)})

    def check_collection(self) -> HealthStatus:
        exists = self.vector_store is not None
        return HealthStatus(
            status="healthy" if exists else "missing", 
            details={"collection_name": getattr(self.vector_store, 'collection_name', 'default'), "exists": exists}
        )

    def get_vector_count(self) -> int:
        return len(self.vector_store.points) if self.vector_store else 0
