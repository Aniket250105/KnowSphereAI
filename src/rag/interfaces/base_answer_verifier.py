from abc import ABC, abstractmethod
from src.models.evaluation_result import VerificationResult
from src.models.rag_response import RAGResponse

class BaseAnswerVerifier(ABC):
    @abstractmethod
    def verify(self, response: RAGResponse) -> VerificationResult:
        """Acts as a final quality gate, checking for obvious errors in the response."""
        pass
