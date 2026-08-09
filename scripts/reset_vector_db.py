import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vectorstore.collection_manager import CollectionManager
from src.core.logger import get_logger
from src.embeddings.embedding_service import EmbeddingService

logger = get_logger(__name__)

def reset_db():
    manager = CollectionManager()
    
    print(f"Checking collection '{manager.collection_name}'...")
    
    if manager.collection_exists():
        print(f"Collection exists with {manager.get_vector_count()} vectors.")
        manager.delete_collection()
        print("Collection deleted.")
    else:
        print("Collection does not exist.")
        
    print("Recreating collection...")
    embed_service = EmbeddingService()
    dim = embed_service.get_embedding_dimension()
    manager.recreate_collection(dimension=dim)
    
    if manager.collection_exists() and manager.get_vector_count() == 0:
        print("\n✅ Vector DB successfully reset and empty collection recreated.")
    else:
        print("\n❌ Failed to reset Vector DB.")

if __name__ == "__main__":
    reset_db()
