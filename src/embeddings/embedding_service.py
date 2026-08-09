from typing import List
from src.embeddings.base_embedding_model import BaseEmbeddingModel
from src.embeddings.embedding_model import EmbeddingModel

class EmbeddingService:
    def __init__(self, model: BaseEmbeddingModel = None):
        # Uses DI if provided, else defaults to the Singleton
        self._model = model or EmbeddingModel()
        
    def embed_text(self, text: str) -> List[float]:
        return self._model.embed_text(text)
        
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        return self._model.embed_batch(texts)
        
    def get_embedding_dimension(self) -> int:
        return self._model.get_dimension()
