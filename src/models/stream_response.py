from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class StreamEvent:
    type: str  # "token" | "metadata" | "error"
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
