import uuid
from typing import Dict, List
from src.memory.conversation_memory import ConversationMemory
from src.database.repository import DatabaseRepository
from src.core.logger import get_logger

logger = get_logger(__name__)

class SessionManager:
    """
    Manages multiple conversation sessions, allowing isolated memory per user/session.
    """
    
    def __init__(self, db_repository: DatabaseRepository):
        self.db = db_repository
        self.sessions: Dict[str, ConversationMemory] = {}
        
    def create_session(self) -> str:
        """
        Creates a new session and returns its unique ID.
        """
        import asyncio
        session_id = str(uuid.uuid4())
        
        async def _do_create():
            from src.database.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                from src.database.repository import DatabaseRepository
                repo = DatabaseRepository(session)
                await repo.create_session(session_id)
                
        asyncio.run(_do_create())
        self.sessions[session_id] = ConversationMemory()
        logger.info(f"Created new session: {session_id}")
        return session_id

        
    def get_memory(self, session_id: str) -> ConversationMemory:
        """
        Retrieves the ConversationMemory for a given session ID.
        Creates it if it does not exist.
        """
        import asyncio
        if session_id not in self.sessions:
            logger.info(f"Loading session {session_id} from database.")
            
            async def _do_get():
                from src.database.database import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    from src.database.repository import DatabaseRepository
                    repo = DatabaseRepository(session)
                    return await repo.get_session_messages(session_id)
                    
            db_messages = asyncio.run(_do_get())
            initial_history = [{"role": m.role, "content": m.content} for m in db_messages]
            self.sessions[session_id] = ConversationMemory(initial_history=initial_history)
            
        return self.sessions[session_id]

        
    def add_user_message(self, session_id: str, message: str) -> int:
        import asyncio
        async def _do_add():
            from src.database.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                from src.database.repository import DatabaseRepository
                repo = DatabaseRepository(session)
                return await repo.save_message(session_id, "user", message)
                
        db_msg = asyncio.run(_do_add())
        mem = self.get_memory(session_id)
        mem.add_user_message(message)
        return db_msg.id
        
    def add_assistant_message(self, session_id: str, message: str) -> int:
        import asyncio
        async def _do_add():
            from src.database.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                from src.database.repository import DatabaseRepository
                repo = DatabaseRepository(session)
                return await repo.save_message(session_id, "assistant", message)
                
        db_msg = asyncio.run(_do_add())
        mem = self.get_memory(session_id)
        mem.add_assistant_message(message)
        return db_msg.id

        
    def clear_session(self, session_id: str):
        """
        Deletes a session from memory.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
