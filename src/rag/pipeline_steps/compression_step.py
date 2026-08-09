from src.rag.compression.context_compressor import SimpleContextCompressor
from src.rag.ranking.context_ranker import ContextRanker
from src.models.search_result import SearchResponse
from src.core import config
from src.rag.context_builder import ContextBuilder

class CompressionStep:
    def __init__(self):
        self.ranker = ContextRanker()
        self.compressor = SimpleContextCompressor()
        
    def execute(self, search_response: SearchResponse) -> dict:
        """
        Ranks, compresses, and builds the final context string.
        Returns a dict with 'compressed_response', 'context_string', 'metrics'.
        """
        if not search_response or not search_response.results:
            return {
                "compressed_response": search_response,
                "context_string": "",
                "metrics": {
                    "original_chunks": 0,
                    "compressed_chunks": 0,
                    "compression_ratio": 1.0
                }
            }
            
        original_count = len(search_response.results)
        
        # 1. Rank
        ranked_response = self.ranker.rank(search_response)
        
        # 2. Compress
        max_length = getattr(config, "MAX_CONTEXT_LENGTH", 4000)
        compressed_response = self.compressor.compress(ranked_response, max_length)
        
        compressed_count = len(compressed_response.results)
        compression_ratio = compressed_count / original_count if original_count > 0 else 1.0
        
        # 3. Build Context String
        context_string = ContextBuilder.build(compressed_response)
        
        return {
            "compressed_response": compressed_response,
            "context_string": context_string,
            "metrics": {
                "original_chunks": original_count,
                "compressed_chunks": compressed_count,
                "compression_ratio": round(compression_ratio, 2)
            }
        }
