from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
import re
from src.core.logger import get_logger

logger = get_logger(__name__)

class HybridSearch:
    def __init__(self, k: int = 60):
        self.k = k

    def fuse(
        self,
        query: str,
        dense_results: List[Tuple[Dict[str, Any], float]]
    ) -> List[Tuple[Dict[str, Any], float]]:
        if not dense_results:
            return []
            
        # 1. Prepare corpus and tokenize
        corpus = [res[0].get("chunk_text", "") for res in dense_results]
        tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        tokenized_query = self._tokenize(query)
        
        # 2. BM25 Scoring
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(tokenized_query)
        
        # Create BM25 ranking (index, score), sorted descending
        bm25_ranked = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True)
        
        # Map original index to BM25 rank (1-indexed)
        bm25_ranks = {original_idx: rank + 1 for rank, (original_idx, score) in enumerate(bm25_ranked)}
        
        # 3. RRF Combination
        rrf_scores = []
        for dense_rank, (original_idx, dense_score) in enumerate(enumerate(dense_results), 1):
            dense_term = 1.0 / (self.k + dense_rank)
            bm25_term = 1.0 / (self.k + bm25_ranks[original_idx])
            rrf_score = dense_term + bm25_term
            rrf_scores.append((dense_results[original_idx][0], rrf_score))
            
        # 4. Sort by RRF score descending
        rrf_sorted = sorted(rrf_scores, key=lambda x: x[1], reverse=True)
        
        logger.info("Hybrid search RRF applied successfully.")
        return rrf_sorted

    def _tokenize(self, text: str) -> List[str]:
        # Simple word tokenization for BM25
        return re.findall(r'\b\w+\b', text.lower())
