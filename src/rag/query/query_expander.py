import re
from src.rag.interfaces.base_query_expander import BaseQueryExpander

class QueryExpander(BaseQueryExpander):
    def __init__(self):
        # Basic abbreviation dictionary for enterprise context
        self.abbreviations = {
            "ai": "artificial intelligence",
            "llm": "large language model",
            "os": "operating system",
            "db": "database",
            "api": "application programming interface",
            "ml": "machine learning",
            "nlp": "natural language processing"
        }
        
        # Simple synonym map
        self.synonyms = {
            "error": ["bug", "issue", "failure"],
            "fast": ["quick", "rapid", "high-performance"],
            "fix": ["resolve", "repair", "patch"]
        }
        
        # Simple spell correction (hardcoded common typos)
        self.spell_corrections = {
            "teh": "the",
            "artifical": "artificial",
            "intelegence": "intelligence"
        }

    def _normalize(self, text: str) -> str:
        """Removes excessive whitespace and lowercases."""
        return re.sub(r'\s+', ' ', text.lower()).strip()

    def _expand_abbreviations(self, tokens: list[str]) -> list[str]:
        expanded = []
        for token in tokens:
            expanded.append(token)
            if token in self.abbreviations:
                expanded.extend(self.abbreviations[token].split())
        return expanded

    def _correct_spelling(self, tokens: list[str]) -> list[str]:
        return [self.spell_corrections.get(token, token) for token in tokens]
        
    def _expand_synonyms(self, tokens: list[str]) -> list[str]:
        expanded = set(tokens)
        for token in tokens:
            if token in self.synonyms:
                expanded.update(self.synonyms[token])
        return list(expanded)

    def expand(self, query: str) -> str:
        """Applies a chain of expansion strategies."""
        normalized = self._normalize(query)
        tokens = normalized.split()
        
        # 1. Spell correction
        tokens = self._correct_spelling(tokens)
        
        # 2. Abbreviation expansion
        tokens = self._expand_abbreviations(tokens)
        
        # 3. Synonym expansion
        # (Be careful not to explode the query too much, we just append synonyms)
        tokens = self._expand_synonyms(tokens)
        
        # Deduplicate while preserving order mostly
        seen = set()
        final_tokens = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                final_tokens.append(t)
                
        return " ".join(final_tokens)
