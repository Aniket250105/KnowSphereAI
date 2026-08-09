from abc import ABC, abstractmethod
from typing import List
from src.models.evaluation_result import GroundingResult

class BaseGroundingChecker(ABC):
    @abstractmethod
    def check(self, answer: str, retrieved_chunks: List[str]) -> GroundingResult:
        """Calculates grounding score based on overlap between generated answer and context."""
        pass
