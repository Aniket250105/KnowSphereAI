import json
import uuid
from pathlib import Path
from src.core.logger import get_logger
from src.core import config
from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.base_vectorstore import BaseVectorStore
from src.models.vector_point import VectorPoint

logger = get_logger(__name__)

class IndexingService:
    def __init__(self, vector_store: BaseVectorStore, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        
    def index_document(self, json_path: Path):
        logger.info(f"Loading processed document from {json_path}")
        
        if not json_path.exists():
            raise FileNotFoundError(f"Missing JSON file: {json_path}")
            
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            logger.error("Corrupt JSON file.")
            raise ValueError("Corrupt JSON file.")
            
        document = data.get("document", {})
        chunks = data.get("chunks", [])
        
        if not document or not chunks:
            logger.error("Empty document or missing chunks.")
            raise ValueError("Empty document or missing chunks.")
            
        # Duplicate indexing validation
        doc_id = document.get("id")
        if doc_id:
            # We fetch a generic vector array but we don't care about the result score,
            # just if any metadata matches the document_id via filters.
            dummy_vector = [0.0] * self.embedding_service.get_embedding_dimension()
            try:
                existing = self.vector_store.search(
                    query_vector=dummy_vector,
                    top_k=1,
                    filters={"document_id": doc_id}
                )
                if existing:
                    logger.warning(f"Document '{document.get('name')}' is already indexed. Skipping.")
                    return
            except Exception:
                # Collection might not exist yet
                pass
            
        # Collection management is handled by LocalVectorStore internally
        
        # Batch embedding
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_service.embed_batch(texts)
        
        vector_points = []
        for i, chunk in enumerate(chunks):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["id"]))
            
            payload = {
                "document_id": document.get("id"),
                "document_name": document.get("name"),
                "document_type": document.get("type"),
                "document_path": document.get("path", str(json_path)),
                "document_hash": document.get("id"), # ID is derived from hash in Phase 2
                "page": chunk.get("page", 1),
                "chunk_id": chunk["id"],
                "chunk_index": i,
                "chunk_text": chunk["text"],
                "start_position": chunk["metadata"].get("start_position"),
                "end_position": chunk["metadata"].get("end_position"),
                "processed_at": document.get("processed_at"),
                "domain": document.get("domain", "general"),
                "schema_version": config.SUPPORTED_VECTOR_SCHEMA_VERSION,
                "embedding_model": config.EMBEDDING_MODEL
            }
            
            vector_points.append(
                VectorPoint(
                    id=point_id,
                    vector=embeddings[i],
                    payload=payload
                )
            )
            
        self.vector_store.upsert(vector_points)
        logger.info(f"Successfully indexed {len(vector_points)} chunks for document {document.get('name')}")
