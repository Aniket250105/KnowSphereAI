import os
from pathlib import Path
from src.core.logger import get_logger
from src.core import config
from src.database.repository import DatabaseRepository
from src.document_processing.processor import DocumentProcessor
from src.services.indexing_service import IndexingService

logger = get_logger(__name__)

class DocumentManager:
    def __init__(
        self, 
        db_repository: DatabaseRepository,
        document_processor: DocumentProcessor,
        indexing_service: IndexingService
    ):
        self.db = db_repository
        self.processor = document_processor
        self.indexer = indexing_service
        
    async def process_and_index_upload(self, temp_path: Path, filename: str) -> str:
        """
        Coordinates processing, indexing, and database logging.
        Returns document ID.
        """
        logger.info(f"DocumentManager starting pipeline for {filename}")
        
        # 1. Register UPLOAD
        file_ext = temp_path.suffix.lower()
        
        # 2. Process
        processed_doc = self.processor.process(temp_path)
        doc_id = processed_doc.document.id
        
        await self.db.create_document(
            document_id=doc_id,
            document_hash=doc_id,
            filename=filename,
            file_type=file_ext,
            path=str(temp_path),
            chunk_count=processed_doc.document.chunk_count,
            status="PROCESSING"
        )
        
        # 3. Index
        json_path = config.PROCESSED_DIR / f"{filename}.json"
        self.indexer.index_document(json_path)
        
        # 4. Mark Available
        await self.db.update_document_status(doc_id, "INDEXED")
        logger.info(f"DocumentManager finished pipeline for {filename}")
        return doc_id

    async def list_documents(self):
        return await self.db.get_all_documents()
        
    async def get_document(self, document_id: str):
        return await self.db.get_document(document_id)
        
    async def delete_document(self, document_id: str) -> bool:
        doc = await self.db.get_document(document_id)
        if not doc:
            logger.warning(f"Document {document_id} not found in DB.")
            return False
            
        logger.info(f"DocumentManager initiating deletion for {doc.filename}")
        
        # 1. Mark as DELETED in DB
        await self.db.update_document_status(document_id, "DELETED")
        
        # 2. Remove vectors from Qdrant
        self.indexer.vector_store.delete({"document_id": document_id})
        
        # 3. Delete raw file
        raw_path = Path(doc.path)
        if raw_path.exists():
            try:
                os.remove(raw_path)
            except Exception as e:
                logger.error(f"Failed to delete raw file {raw_path}: {e}")
                
        # 4. Delete processed JSON
        json_path = config.PROCESSED_DIR / f"{doc.filename}.json"
        if json_path.exists():
            try:
                os.remove(json_path)
            except Exception as e:
                logger.error(f"Failed to delete processed file {json_path}: {e}")
                
        logger.info(f"Successfully deleted document {document_id}")
        return True
