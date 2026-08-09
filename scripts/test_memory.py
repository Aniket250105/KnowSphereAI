import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rag_pipeline import RAGPipeline
from src.core.logger import get_logger

logger = get_logger(__name__)

def test_memory():
    print("Initializing RAG Pipeline with Session Manager...")
    pipeline = RAGPipeline()
    
    session_id = pipeline.create_session()
    print(f"Session ID created: {session_id}")
    
    print("\n[User]: What is deadlock?")
    response = pipeline.ask("What is deadlock?", session_id=session_id)
    print(f"[AI]: {response.answer}")
    
    print("\n[User]: Give examples")
    response2 = pipeline.ask("Give examples", session_id=session_id)
    print(f"[AI]: {response2.answer}")
    
    print("\n--- Memory Buffer for Session ---")
    print(pipeline.session_manager.get_memory(session_id).get_formatted_history())

if __name__ == "__main__":
    test_memory()
