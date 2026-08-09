import statistics
from src.models.search_result import SearchResponse

class ConfidenceScorer:
    """
    Evaluates retrieval quality to determine an overall confidence score.
    """
    @staticmethod
    def compute_confidence(search_response: SearchResponse) -> str:
        if not search_response or not search_response.results:
            return "LOW"
            
        scores = [res.score for res in search_response.results]
        avg_score = statistics.mean(scores)
        
        # Simple heuristic for confidence
        # For cosine similarity, scores are usually between 0 and 1
        # Hybrid RRF scores can vary based on k, but relative drop-off is key
        
        if avg_score > 0.75 or (len(scores) >= 3 and avg_score > 0.6):
            return "HIGH"
        elif avg_score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
