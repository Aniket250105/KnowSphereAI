from typing import List, Dict, Any
from src.models.evaluation_result import EvaluationResult
from src.models.rag_response import RAGResponse
from src.rag.validation.grounding_checker import GroundingChecker
from src.rag.validation.citation_validator import CitationValidator
from src.rag.validation.answer_verifier import AnswerVerifier
from src.evaluation.hallucination_detector import HallucinationDetector

class ValidationStep:
    def __init__(self):
        self.grounding_checker = GroundingChecker()
        self.citation_validator = CitationValidator()
        self.answer_verifier = AnswerVerifier()
        self.hallucination_detector = HallucinationDetector()
        
    def execute(self, answer: str, retrieved_chunks: List[str], sources: List[Dict[str, Any]], rag_response: RAGResponse) -> EvaluationResult:
        """
        Executes all validation and evaluation checks post-generation.
        """
        grounding = self.grounding_checker.check(answer, retrieved_chunks)
        citation_validation = self.citation_validator.validate(answer, sources)
        hallucination = self.hallucination_detector.detect(answer, retrieved_chunks)
        
        # We need the response object for the verifier, so we attach the partial evaluations first
        eval_result = EvaluationResult(
            grounding=grounding,
            hallucination=hallucination,
            citation_validation=citation_validation,
            verification=None # Will compute next
        )
        rag_response.evaluation = eval_result
        
        verification = self.answer_verifier.verify(rag_response)
        eval_result.verification = verification
        
        # Add warnings from citation validator to the response root if they exist
        if citation_validation.warnings:
            # rag_response schema doesn't have warnings by default but we can add it to evaluation
            pass
            
        return eval_result
