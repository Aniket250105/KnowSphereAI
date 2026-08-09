import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core import config
from src.core.logger import get_logger
from src.document_processing.processor import DocumentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.qdrant_store import QdrantVectorStore
from src.services.indexing_service import IndexingService
from src.vectorstore.collection_manager import CollectionManager

logger = get_logger(__name__)

DOMAIN_MAP = {
    "university_rules.txt": "education",
    "python_basics.txt": "programming",
    "operating_systems.txt": "computer_science",
    "machine_learning.txt": "artificial_intelligence"
}

def run_pipeline():
    # 1. Process documents
    processor = DocumentProcessor()
    raw_files = list(config.RAW_DIR.glob("*.txt"))
    
    docs_processed = 0
    total_chunks = 0
    
    for raw_file in raw_files:
        try:
            logger.info(f"Processing {raw_file.name}...")
            processed_doc = processor.process(raw_file)
            docs_processed += 1
            total_chunks += len(processed_doc.chunks)
            
            # Inject domain metadata into the JSON artifact
            json_path = config.PROCESSED_DIR / f"{raw_file.name}.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                domain = DOMAIN_MAP.get(raw_file.name, "general")
                data["document"]["domain"] = domain
                
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Failed to process {raw_file.name}: {e}")
            
    # 2. Reset Vector DB
    manager = CollectionManager()
    if manager.collection_exists():
        manager.delete_collection()
        
    # 3. Index Documents
    embedding_service = EmbeddingService()
    vector_store = QdrantVectorStore()
    indexer = IndexingService(vector_store=vector_store, embedding_service=embedding_service)
    
    processed_files = list(config.PROCESSED_DIR.glob("*.json"))
    for pf in processed_files:
        try:
            indexer.index_document(pf)
        except Exception as e:
            logger.error(f"Failed to index {pf.name}: {e}")
            
    vectors_stored = manager.get_vector_count()
    
    print("\n" + "="*50)
    print(" MULTI-DOCUMENT INGESTION COMPLETE")
    print("="*50)
    print(f"Documents processed: {docs_processed}")
    print(f"Chunks generated: {total_chunks}")
    print(f"Vectors stored: {vectors_stored}")
    print(f"Collection size: {vectors_stored}")
    print("="*50)

if __name__ == "__main__":
    run_pipeline()
