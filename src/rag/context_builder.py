from src.models.search_result import SearchResponse
from src.core import config
from src.core.logger import get_logger

logger = get_logger(__name__)

class ContextBuilder:
    """
    Constructs a formatted context string from retrieval hits.
    """
    
    @staticmethod
    def build(search_response: SearchResponse) -> str:
        if not search_response or not search_response.results:
            return ""
            
        # Deduplicate chunks to prevent redundant context
        seen_chunks = set()
        unique_results = []
        
        for result in search_response.results:
            if result.chunk_id not in seen_chunks:
                unique_results.append(result)
                seen_chunks.add(result.chunk_id)
                
        # Sort by score descending (Qdrant already does this, but good practice)
        unique_results = sorted(unique_results, key=lambda x: x.score, reverse=True)
        
        context_parts = []
        current_length = 0
        
        for result in unique_results:
            part = (
                f"================================================\n"
                f"Source: {result.document_name}\n"
                f"Page: {result.page}\n"
                f"Chunk: {result.chunk_id}\n"
                f"Similarity: {result.score:.4f}\n\n"
                f"Content:\n{result.text}\n"
                f"================================================\n"
            )
            
            # Simple length heuristic (1 token ~ 4 chars). We constrain length directly on characters for simplicity,
            # or rely on config.MAX_CONTEXT_LENGTH representing characters here.
            # Assuming config.MAX_CONTEXT_LENGTH is a rough char limit, e.g., 4000 chars.
            if current_length + len(part) > config.MAX_CONTEXT_LENGTH:
                logger.warning("Max context length reached, truncating remaining retrieved chunks.")
                break
                
            context_parts.append(part)
            current_length += len(part)
            
        return "\n".join(context_parts)
