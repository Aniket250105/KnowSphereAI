from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class HealthStatus:
    status: str
    details: Dict[str, Any]
