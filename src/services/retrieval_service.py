import time
from typing import Optional, Dict, Any
from src.core import config
from src.core.logger import get_logger
from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.base_vectorstore import BaseVectorStore
from src.models.search_result import SearchResult, SearchResponse
from src.search.hybrid_search import HybridSearch

logger = get_logger(__name__)

class RetrievalService:
    def __init__(self, vector_store: BaseVectorStore, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.hybrid_search = HybridSearch()
        
    def retrieve(
        self, 
        query: str, 
        top_k: int = config.TOP_K_RESULTS, 
        search_mode: str = "hybrid", 
        filters: Dict[str, Any] = None
    ) -> SearchResponse:
        logger.info(f"Executing {search_mode} retrieval for query: '{query}'")
        if not query.strip():
            raise ValueError("Invalid search query: Query cannot be empty.")
            
        start_time = time.time()
        
        # 1. Embedding Stage
        embed_start = time.time()
        query_vector = self.embedding_service.embed_text(query)
        embedding_time = time.time() - embed_start
        
        # 2. Retrieval Stage
        logger.info("Searching vector collection...")
        retrieval_start = time.time()
        
        fetch_k = top_k * 3 if search_mode == "hybrid" else top_k
        
        try:
            raw_results = self.vector_store.search(
                query_vector=query_vector,
                top_k=fetch_k,
                score_threshold=None,
                filters=filters
            )
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise RuntimeError(f"Search engine failure: {e}")
            
        if search_mode == "hybrid" and raw_results:
            raw_results = self.hybrid_search.fuse(query, raw_results)[:top_k]
            
        search_results = []
        for payload, score in raw_results:
            result = SearchResult(
                document_id=payload.get("document_id", ""),
                document_name=payload.get("document_name", ""),
                chunk_id=payload.get("chunk_id", ""),
                text=payload.get("chunk_text", ""),
                page=payload.get("page", 1),
                score=score,
                metadata=payload
            )
            search_results.append(result)
            
        retrieval_time = time.time() - retrieval_start
        search_time = time.time() - start_time
        
        logger.info(f"Returning top {len(search_results)} results in {search_time:.4f} seconds.")
        
        return SearchResponse(
            query=query,
            results=search_results,
            total_results=len(search_results),
            search_time_seconds=search_time,
            embedding_time_seconds=embedding_time,
            retrieval_time_seconds=retrieval_time
        )
