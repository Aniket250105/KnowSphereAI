import re
from typing import List
from src.rag.interfaces.base_grounding_checker import BaseGroundingChecker
from src.models.evaluation_result import GroundingResult

class GroundingChecker(BaseGroundingChecker):
    def _extract_words(self, text: str) -> set:
        """Extracts unique lowercase alphanumeric words of length > 3 to avoid stop words."""
        words = re.findall(r'\b[a-zA-Z0-9]{4,}\b', text.lower())
        return set(words)
        
    def _calculate_jaccard(self, set1: set, set2: set) -> float:
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def check(self, answer: str, retrieved_chunks: List[str]) -> GroundingResult:
        if not answer or not retrieved_chunks:
            return GroundingResult(0.0, "LOW", 0.0, 0.0, 0.0)

        combined_context = " ".join(retrieved_chunks)
        
        answer_words = self._extract_words(answer)
        context_words = self._extract_words(combined_context)
        
        # 1. Context Coverage (How much of the answer is found in the context?)
        # Using simple inclusion ratio instead of Jaccard for coverage
        if not answer_words:
            context_coverage = 0.0
        else:
            intersection = answer_words.intersection(context_words)
            context_coverage = len(intersection) / len(answer_words)

        # 2. Citation Coverage (Does the answer use [1], [2] formatting?)
        citations = re.findall(r'\[\d+\]', answer)
        # Simple heuristic: if citations exist, coverage is high, otherwise 0
        citation_coverage = min(1.0, len(set(citations)) * 0.5) if citations else 0.0
        
        # 3. Semantic Similarity (Proxy using Jaccard Similarity of larger bi-grams could be better, but we use word sets here)
        semantic_similarity = self._calculate_jaccard(answer_words, context_words)
        
        # We boost semantic similarity since Jaccard is naturally very low between a short answer and huge context
        semantic_similarity = min(1.0, semantic_similarity * 3)
        
        # Composite Score
        score = (0.40 * context_coverage) + (0.30 * citation_coverage) + (0.30 * semantic_similarity)
        
        # Define Boundaries
        if score >= 0.85:
            level = "HIGH"
        elif score >= 0.60:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        return GroundingResult(
            score=round(score, 4),
            level=level,
            context_coverage=round(context_coverage, 4),
            citation_coverage=round(citation_coverage, 4),
            semantic_similarity=round(semantic_similarity, 4)
        )
