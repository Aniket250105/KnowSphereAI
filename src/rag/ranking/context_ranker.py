from collections import defaultdict
from src.rag.interfaces.base_ranker import BaseContextRanker
from src.models.search_result import SearchResponse

class ContextRanker(BaseContextRanker):
    def rank(self, search_response: SearchResponse) -> SearchResponse:
        if not search_response or not search_response.results:
            return search_response

        doc_counts = defaultdict(int)
        
        # We apply penalties for document diversity
        # The more chunks from the same document, the lower their subsequent score becomes.
        # DIVERSITY_PENALTY = 0.05 per chunk seen from the same doc.
        
        for result in search_response.results:
            doc_id = result.document_id
            count = doc_counts[doc_id]
            
            # Position penalty: later pages or chunks might be slightly less relevant than introductory ones
            # Very small heuristic adjustment
            page = result.page
            position_penalty = (page * 0.001) if page else 0
            
            diversity_penalty = count * 0.05
            
            # Adjust score
            result.score = result.score - diversity_penalty - position_penalty
            
            # Ensure score doesn't drop below 0
            result.score = max(0.0, result.score)
            
            doc_counts[doc_id] += 1
            
        # Re-sort based on adjusted score
        search_response.results = sorted(search_response.results, key=lambda x: x.score, reverse=True)
        
        return search_response
