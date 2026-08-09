from abc import ABC, abstractmethod

class BaseQueryExpander(ABC):
    @abstractmethod
    def expand(self, query: str) -> str:
        """Expands a query based on synonyms, spell correction, or abbreviations."""
        pass
