import sys
import time
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core import config
from src.core.logger import get_logger
from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.qdrant_store import QdrantVectorStore
from src.services.indexing_service import IndexingService
from src.services.retrieval_service import RetrievalService
from src.services.health_service import HealthService

logger = get_logger(__name__)

def main():
    processed_dir = config.PROCESSED_DIR
    sample_json = processed_dir / "sample.txt.json"
    
    if not sample_json.exists():
        logger.error(f"Sample JSON not found at {sample_json}.")
        return

    # Override config to recreate the collection on each test run
    config.COLLECTION_RECREATE = True
    
    # 2. Dependency Injection Setup
    embedding_service = EmbeddingService()
    vector_store = QdrantVectorStore()
    
    indexer = IndexingService(vector_store=vector_store, embedding_service=embedding_service)
    retriever = RetrievalService(vector_store=vector_store, embedding_service=embedding_service)
    health = HealthService()
    
    # 3. Check Health
    print("\n=== SYSTEM HEALTH ===")
    print(f"Embedding: {health.check_embedding_model().status}")
    print(f"Vector DB: {health.check_vector_database().status}")
    
    # 4. Indexing Pipeline
    print("\n=== STARTING INDEXING PIPELINE ===")
    start_idx = time.time()
    try:
        indexer.index_document(sample_json)
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        return
    idx_time = time.time() - start_idx
    
    dim = embedding_service.get_embedding_dimension()
    count = health.get_vector_count()
    
    print("\n=========================================")
    print(" INDEXING SUMMARY")
    print("=========================================")
    print(f"Embedding model     : {config.EMBEDDING_MODEL}")
    print(f"Embedding dimension : {dim}")
    print(f"Indexed chunk count : {count}")
    print(f"Indexing time       : {idx_time:.4f} seconds")
    
    # 5. Semantic Search Pipeline
    queries = [
        "What is artificial intelligence?",
        "Explain machine learning.",
        "Attendance requirements",
        "Operating systems",
        "Python loops"
    ]
    
    print("\n=========================================")
    print(" SEARCH PIPELINE")
    print("=========================================\n")
    
    for q in queries:
        try:
            response = retriever.retrieve(q, top_k=2)
            
            print(f"Query: '{response.query}'")
            print(f"Search Time: {response.search_time_seconds:.4f}s (Embed: {response.embedding_time_seconds:.4f}s, DB: {response.retrieval_time_seconds:.4f}s)")
            
            if not response.results:
                print("  No results found.")
                
            for i, res in enumerate(response.results):
                print(f"  [{i+1}] Score: {res.score:.4f} | Document: {res.document_name}")
                snippet = res.text[:80].replace('\n', ' ') + "..."
                print(f"      Text: {snippet}")
            print("-" * 50)
            
        except Exception as e:
            logger.error(f"Search failed for '{q}': {e}")

if __name__ == "__main__":
    main()
