from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class HealthResponse(BaseModel):
    api_status: str
    embedding_model_status: str
    vector_db_status: str
    llm_status: str
    
class UploadResponse(BaseModel):
    filename: str
    document_id: str
    chunk_count: int
    status: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    
class ChatSource(BaseModel):
    document: str
    page: int
    chunk_id: str
    score: float
    position: Optional[str] = None
    
class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]
    retrieved_chunks: List[str]
    generation_time_seconds: float
    total_time_seconds: float
    confidence: str
    suggested_questions: List[str]

class FeedbackRequest(BaseModel):
    message_id: int
    rating: str
    comment: Optional[str] = None
