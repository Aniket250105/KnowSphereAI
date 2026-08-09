import time
from pathlib import Path
from typing import Union
from datetime import datetime, timezone

from src.core.logger import get_logger
from src.core import config
from src.models.document import ProcessedDocument, DocumentMetadata
from src.document_processing.base import BaseDocumentLoader
from src.document_processing.loaders import PDFLoader, TXTLoader, DOCXLoader
from src.document_processing.cleaner import DocumentCleaner
from src.document_processing.chunker import FixedSizeChunker
from src.document_processing.exporter import JSONExporter

logger = get_logger(__name__)

class DocumentProcessor:
    """
    Orchestrates the loading, cleaning, chunking, and exporting of documents.
    """
    
    def __init__(
        self, 
        output_dir: Union[Path, str] = config.PROCESSED_DIR,
        chunk_size: int = config.CHUNK_SIZE, 
        chunk_overlap: int = config.CHUNK_OVERLAP
    ):
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.cleaner = DocumentCleaner()
        self.chunker = FixedSizeChunker(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        self.exporter = JSONExporter(output_dir=self.output_dir)
        
    def _get_loader(self, file_path: Path) -> BaseDocumentLoader:
        """Determines the appropriate loader based on file extension."""
        ext = file_path.suffix.lower()
        if ext == '.pdf':
            return PDFLoader()
        elif ext == '.txt':
            return TXTLoader()
        elif ext == '.docx':
            return DOCXLoader()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def process(self, file_path: Union[Path, str]) -> ProcessedDocument:
        """
        Processes a document end-to-end and measures processing time.
        
        Args:
            file_path (Union[Path, str]): Path to the document.
            
        Returns:
            ProcessedDocument: The processed document object containing chunks and metadata.
        """
        path = Path(file_path)
        logger.info(f"Starting processing for: {path.name}")
        start_time = time.time()
        
        if not path.exists():
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")
            
        # 1. Load
        loader = self._get_loader(path)
        document = loader.load(path)
        
        # 2. Clean
        cleaned_document = self.cleaner.clean(document)
        logger.info(f"Cleaned document {path.name}")
        
        # 3. Chunk
        chunks = self.chunker.chunk(cleaned_document)
        logger.info(f"Generated {len(chunks)} chunks")
        
        # Build DocumentMetadata
        document_metadata = DocumentMetadata(
            id=cleaned_document.id,
            name=cleaned_document.name,
            type=cleaned_document.file_type,
            path=cleaned_document.path,
            pages=cleaned_document.pages,
            characters=cleaned_document.characters,
            created_at=cleaned_document.created_at,
            modified_at=cleaned_document.modified_at,
            processed_at=datetime.now(timezone.utc).isoformat(),
            chunk_count=len(chunks),
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            version=config.DOCUMENT_SCHEMA_VERSION
        )
        
        processed_doc = ProcessedDocument(
            document=document_metadata,
            chunks=chunks
        )
        
        # 4. Export
        self.exporter.export(processed_doc)
        logger.info(f"Exported JSON for {path.name}")
        
        end_time = time.time()
        logger.info(f"Total processing time: {end_time - start_time:.2f} seconds")
        
        return processed_doc
