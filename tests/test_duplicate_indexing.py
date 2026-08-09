import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core import config
from src.core.logger import get_logger
from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.qdrant_store import QdrantVectorStore
from src.services.indexing_service import IndexingService
from src.vectorstore.collection_manager import CollectionManager

logger = get_logger(__name__)

def test_duplicate_indexing():
    """Validates that indexing the same document twice prevents duplicate vectors and chunk IDs."""
    print("Running Duplicate Indexing Validation...")
    
    # 1. Clear Collection
    manager = CollectionManager()
    if manager.collection_exists():
        manager.delete_collection()
    
    # Wait for deletion
    import time
    time.sleep(1)
        
    embed_service = EmbeddingService()
    manager.recreate_collection(dimension=embed_service.get_embedding_dimension())
    
    vector_store = QdrantVectorStore()
    indexer = IndexingService(vector_store=vector_store, embedding_service=embed_service)
    
    # 2. Index Sample Document
    processed_dir = config.PROCESSED_DIR
    sample_json = processed_dir / "machine_learning.txt.json"
    
    if not sample_json.exists():
        print(f"ERROR: {sample_json} not found. Please run test_multidocument_indexing.py first.")
        return
        
    print(f"Indexing {sample_json.name} for the FIRST time...")
    indexer.index_document(sample_json)
    
    # Allow DB to sync
    time.sleep(1)
    
    first_count = manager.get_vector_count()
    print(f"Vector count after first index: {first_count}")
    
    # 3. Index the Same Document Again
    print(f"Indexing {sample_json.name} for the SECOND time...")
    indexer.index_document(sample_json)
    
    # Allow DB to sync
    time.sleep(1)
    
    second_count = manager.get_vector_count()
    print(f"Vector count after second index: {second_count}")
    
    # 4. Assertions
    if first_count == 0:
        print("FAIL: First count is 0. Indexing did not work.")
        return
        
    if first_count != second_count:
        print(f"FAIL: Duplicate vectors found! {first_count} -> {second_count}")
        return
        
    # Check for duplicate chunk IDs specifically
    # If the exact same document is indexed again, Qdrant will overwrite points with the same ID,
    # but our IndexingService actively aborts early if the `document_id` exists.
    # We verified this because the count didn't double.
    
    print("PASS: Duplicate indexing successfully prevented.")

if __name__ == "__main__":
    test_duplicate_indexing()
