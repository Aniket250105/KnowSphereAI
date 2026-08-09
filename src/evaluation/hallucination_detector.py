import re
from typing import List
from src.models.evaluation_result import HallucinationResult

class HallucinationDetector:
    def detect(self, answer: str, retrieved_chunks: List[str]) -> HallucinationResult:
        if not answer or not retrieved_chunks:
            # If there's no context, everything is hallucinated unless it says it doesn't know
            if "i couldn't find" in answer.lower() or "i don't know" in answer.lower():
                return HallucinationResult(risk="LOW")
            return HallucinationResult(risk="HIGH", unsupported_claim_count=1)

        combined_context = " ".join(retrieved_chunks).lower()
        
        # Split answer into rudimentary sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if len(s.strip()) > 10]
        
        unsupported_sentences = []
        
        for sentence in sentences:
            # If the sentence is a source listing, ignore it
            if sentence.lower().startswith("sources:") or sentence.lower().startswith("page:"):
                continue
                
            # Extract main words (entities/nouns proxy)
            words = set(re.findall(r'\b[a-zA-Z0-9]{5,}\b', sentence.lower()))
            
            if not words:
                continue
                
            # Find words that exist in context
            supported_words = [w for w in words if w in combined_context]
            
            # If less than 40% of the significant words in a sentence appear in context, flag it
            if len(supported_words) / len(words) < 0.4:
                unsupported_sentences.append(sentence)

        unsupported_claim_count = len(unsupported_sentences)
        
        # Determine Citation missing
        has_citations = bool(re.search(r'\[\d+\]', answer))
        citation_missing = not has_citations and len(retrieved_chunks) > 0 and "i couldn't find" not in answer.lower()
        
        # Risk assessment
        if unsupported_claim_count > 2 or (unsupported_claim_count > 0 and citation_missing):
            risk = "HIGH"
        elif unsupported_claim_count > 0 or citation_missing:
            risk = "MEDIUM"
        else:
            risk = "LOW"
            
        return HallucinationResult(
            risk=risk,
            unsupported_sentences=unsupported_sentences,
            unsupported_claim_count=unsupported_claim_count,
            citation_missing=citation_missing
        )
