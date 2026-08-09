from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GroundingResult:
    score: float
    level: str  # HIGH, MEDIUM, LOW
    context_coverage: float
    citation_coverage: float
    semantic_similarity: float

@dataclass
class HallucinationResult:
    risk: str  # LOW, MEDIUM, HIGH
    unsupported_sentences: List[str] = field(default_factory=list)
    unsupported_claim_count: int = 0
    citation_missing: bool = False

@dataclass
class CitationValidationResult:
    valid_sources: List[str] = field(default_factory=list)
    removed_sources: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class VerificationResult:
    passed: bool
    reasons: List[str] = field(default_factory=list)

@dataclass
class EvaluationResult:
    grounding: Optional[GroundingResult] = None
    hallucination: Optional[HallucinationResult] = None
    citation_validation: Optional[CitationValidationResult] = None
    verification: Optional[VerificationResult] = None
