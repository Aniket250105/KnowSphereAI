import threading
from typing import List
import numpy as np

from src.core import config
from src.core.logger import get_logger
from src.embeddings.base_embedding_model import BaseEmbeddingModel

logger = get_logger(__name__)

class EmbeddingModel(BaseEmbeddingModel):
    """
    Singleton for loading and providing the SentenceTransformer model lazily.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingModel, cls).__new__(cls)
                    cls._instance._model = None
        return cls._instance
        
    def _get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL} on device: {config.EMBEDDING_DEVICE}")
                    from sentence_transformers import SentenceTransformer
                    self._model = SentenceTransformer(
                        config.EMBEDDING_MODEL, 
                        device=config.EMBEDDING_DEVICE
                    )
        return self._model

    def embed_text(self, text: str) -> List[float]:
        model = self._get_model()
        embedding = model.encode(text, normalize_embeddings=config.NORMALIZE_EMBEDDINGS)
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        logger.info("Embedding batch started")
        embeddings = model.encode(
            texts, 
            batch_size=config.EMBEDDING_BATCH_SIZE, 
            normalize_embeddings=config.NORMALIZE_EMBEDDINGS
        )
        logger.info(f"Generated embeddings for {len(texts)} texts")
        if isinstance(embeddings, np.ndarray):
            return embeddings.tolist()
        return list(embeddings)

    def get_dimension(self) -> int:
        model = self._get_model()
        return model.get_sentence_embedding_dimension()
