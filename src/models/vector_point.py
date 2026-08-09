from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class VectorPoint:
    """
    Represents a vector point ready to be inserted into the vector database.
    
    Attributes:
        id (str): Unique identifier for the chunk/vector (often mapped from chunk_id).
        vector (List[float]): The generated embedding.
        payload (Dict[str, Any]): Metadata associated with the vector (e.g. document details, text).
    """
    id: str
    vector: List[float]
    payload: Dict[str, Any]
