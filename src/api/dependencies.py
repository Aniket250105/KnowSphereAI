from src.document_processing.processor import DocumentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.local_store import LocalVectorStore
from src.services.indexing_service import IndexingService
from src.rag.rag_pipeline import RAGPipeline
from src.database.database import AsyncSessionLocal, init_db, get_db

from src.database.repository import DatabaseRepository
from src.documents.document_manager import DocumentManager
from src.memory.session_manager import SessionManager
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.auth.jwt_handler import decode_token
from src.database.models import UserModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        raise credentials_exception
        
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception
    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# Singletons for API dependency injection
_document_processor = None
_embedding_service = None
_vector_store = None
_indexing_service = None

# Initialize DB is handled in run.py

def get_db_repository(db: AsyncSession = Depends(get_db)) -> DatabaseRepository:
    return DatabaseRepository(db)

def get_document_processor() -> DocumentProcessor:
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_vector_store() -> LocalVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = LocalVectorStore()
    return _vector_store

def get_indexing_service() -> IndexingService:
    global _indexing_service
    if _indexing_service is None:
        _indexing_service = IndexingService(get_vector_store(), get_embedding_service())
    return _indexing_service

def get_document_manager(db: AsyncSession = Depends(get_db)) -> DocumentManager:
    return DocumentManager(
        DatabaseRepository(db),
        get_document_processor(),
        get_indexing_service()
    )

def get_session_manager() -> SessionManager:
    return SessionManager(None)

def get_rag_pipeline(session_manager: SessionManager = Depends(get_session_manager)) -> RAGPipeline:
    return RAGPipeline(session_manager)
