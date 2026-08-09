from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models.evaluation_result import CitationValidationResult

class BaseCitationValidator(ABC):
    @abstractmethod
    def validate(self, answer: str, sources: List[Dict[str, Any]]) -> CitationValidationResult:
        """Ensures all citations in the answer correspond to actual provided sources."""
        pass
