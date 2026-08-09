import re
from typing import List, Dict
from src.rag.interfaces.base_compressor import BaseContextCompressor
from src.models.search_result import SearchResponse, SearchResult
from src.core.logger import get_logger

logger = get_logger(__name__)

class SimpleContextCompressor(BaseContextCompressor):
    def compress(self, search_response: SearchResponse, max_length: int) -> SearchResponse:
        if not search_response or not search_response.results:
            return search_response

        # 1. Deduplicate by chunk_id and text content
        unique_results = []
        seen_chunks = set()
        seen_texts = set()

        for result in search_response.results:
            if result.chunk_id not in seen_chunks and result.text not in seen_texts:
                unique_results.append(result)
                seen_chunks.add(result.chunk_id)
                seen_texts.add(result.text)

        # 2. Sort by similarity score descending to prioritize best chunks
        sorted_results = sorted(unique_results, key=lambda x: x.score, reverse=True)

        # 3. Merge contiguous chunks if possible
        # This requires identifying chunk sequence numbers from chunk_ids (e.g., doc_id_0, doc_id_1)
        # We will map chunks by document and try to group them, then re-sort by best score in group.
        # For simplicity, we just enforce length limits here. Merging overlapping text is complex without knowing exact offsets.
        # We will truncate when max_length is reached.
        
        compressed_results = []
        current_length = 0

        for result in sorted_results:
            # Estimate character length roughly
            part_length = len(result.text)
            
            if current_length + part_length > max_length:
                # If even the first chunk is too big, truncate it
                if not compressed_results:
                    result.text = result.text[:max_length] + "..."
                    compressed_results.append(result)
                logger.info(f"Context compressed to {len(compressed_results)} chunks (limit: {max_length} chars).")
                break
                
            compressed_results.append(result)
            current_length += part_length

        return SearchResponse(
            query=search_response.query,
            results=compressed_results,
            total_results=len(compressed_results),
            search_time_seconds=search_response.search_time_seconds,
            embedding_time_seconds=search_response.embedding_time_seconds,
            retrieval_time_seconds=search_response.retrieval_time_seconds
        )
