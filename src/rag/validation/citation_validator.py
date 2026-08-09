import re
from typing import List, Dict, Any
from src.rag.interfaces.base_validator import BaseCitationValidator
from src.models.evaluation_result import CitationValidationResult

class CitationValidator(BaseCitationValidator):
    def validate(self, answer: str, sources: List[Dict[str, Any]]) -> CitationValidationResult:
        warnings = []
        valid_sources = []
        removed_sources = []
        
        # Extract inline citations like [1], [2]
        inline_citations = re.findall(r'\[(\d+)\]', answer)
        cited_indices = set(int(idx) for idx in inline_citations)
        
        # Sources are typically 1-indexed in the prompt
        available_indices = set(range(1, len(sources) + 1))
        
        for idx in cited_indices:
            if idx in available_indices:
                valid_sources.append(str(idx))
            else:
                removed_sources.append(str(idx))
                warnings.append(f"Citation [{idx}] found in text but no corresponding source provided.")
                
        # We also could strip invalid citations from the answer string, but the interface 
        # doesn't return the modified answer. For Phase 8A, identifying the warnings is sufficient.
        
        return CitationValidationResult(
            valid_sources=valid_sources,
            removed_sources=removed_sources,
            warnings=warnings
        )
