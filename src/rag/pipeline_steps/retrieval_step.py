from src.services.retrieval_service import RetrievalService
from src.rag.query.query_expander import QueryExpander
from src.evaluation.confidence import ConfidenceScorer
from src.models.search_result import SearchResponse
from src.core import config
from src.core.logger import get_logger

logger = get_logger(__name__)

class RetrievalStep:
    def __init__(self, retrieval_service: RetrievalService):
        self.retrieval_service = retrieval_service
        self.query_expander = QueryExpander()
        # Default MAX_RETRIES to 2 if not set
        self.max_retries = int(getattr(config, "MAX_RETRIEVAL_RETRIES", "2"))
        
    def execute(self, query: str) -> dict:
        """
        Executes retrieval with an automatic retry strategy on low confidence.
        Returns a dict with 'search_response', 'confidence', 'retry_count', 'expanded_query'.
        """
        retry_count = 0
        expanded_query = query
        top_k = config.TOP_K_RESULTS
        
        while retry_count <= self.max_retries:
            search_response = self.retrieval_service.retrieve(expanded_query, top_k=top_k, search_mode="hybrid")
            confidence = ConfidenceScorer.compute_confidence(search_response)
            
            if confidence in ["HIGH", "MEDIUM"] or retry_count == self.max_retries:
                return {
                    "search_response": search_response,
                    "confidence": confidence,
                    "retry_count": retry_count,
                    "expanded_query": expanded_query if expanded_query != query else None
                }
                
            # Retry Strategy
            retry_count += 1
            logger.info(f"Retrieval confidence LOW. Retrying (Attempt {retry_count})...")
            
            if retry_count == 1:
                top_k += 5
            elif retry_count == 2:
                top_k += 10
                expanded_query = self.query_expander.expand(query)
                
        # Fallback
        return {
            "search_response": None,
            "confidence": "LOW",
            "retry_count": retry_count,
            "expanded_query": None
        }
