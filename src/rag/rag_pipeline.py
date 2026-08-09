from src.core.logger import get_logger
from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.local_store import LocalVectorStore
from src.services.retrieval_service import RetrievalService
from src.llm.llm_service import LLMService
from src.services.rag_service import RAGService
from src.memory.session_manager import SessionManager
from typing import Iterator
from src.models.stream_response import StreamEvent

logger = get_logger(__name__)

class RAGPipeline:
    """
    High-level facade for the entire Retrieval-Augmented Generation system.
    Instantiates necessary services and exposes a simple .ask() interface.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RAGPipeline, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, session_manager: SessionManager):
        if self._initialized:
            return
            
        logger.info("Initializing RAG Pipeline...")
        # Retrieval Dependencies
        self.embedding_service = EmbeddingService()
        self.vector_store = LocalVectorStore()
        self.retrieval_service = RetrievalService(self.vector_store, self.embedding_service)
        
        # LLM Dependencies
        self.llm_service = LLMService()
        
        # Orchestrator
        self.rag_service = RAGService(self.retrieval_service, self.llm_service)
        
        # Sessions (injected)
        self.session_manager = session_manager
        
        self._initialized = True
        
    def create_session(self) -> str:
        """Create a new chat session and return its ID."""
        return self.session_manager.create_session()
        
    def ask(self, query: str, session_id: str = "default"):
        memory = self.session_manager.get_memory(session_id)
        
        # 1. Add user query to memory
        self.session_manager.add_user_message(session_id, query)
        
        # 2. Get RAG response
        response = self.rag_service.ask(query, memory=memory)
        
        # 3. Add AI answer to memory
        msg_id = self.session_manager.add_assistant_message(session_id, response.answer)
        
        return response
        
    def ask_stream(self, query: str, session_id: str = "default") -> Iterator[StreamEvent]:
        memory = self.session_manager.get_memory(session_id)
        self.session_manager.add_user_message(session_id, query)
        
        full_answer = ""
        
        for event in self.rag_service.ask_stream(query, memory=memory):
            if event.type == "token" and event.content:
                full_answer += event.content
                yield event
            elif event.type == "metadata":
                # Generation complete, save to memory
                msg_id = self.session_manager.add_assistant_message(session_id, full_answer)
                event.metadata["message_id"] = msg_id
                yield event
            else:
                yield event
        
    def clear_session(self, session_id: str = "default"):
        """Reset the conversation history for a specific session."""
        self.session_manager.clear_session(session_id)
