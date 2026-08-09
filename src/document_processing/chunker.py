from typing import List
from src.core.logger import get_logger
from src.models.document import Document, Chunk, ChunkMetadata
from src.document_processing.base import BaseChunker

logger = get_logger(__name__)

class FixedSizeChunker(BaseChunker):
    """
    Chunks text into fixed-size character sequences with overlap.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Splits the document's content into chunks based on fixed sizes.
        
        Args:
            document (Document): The document to chunk.
            
        Returns:
            List[Chunk]: A list of Chunk objects.
        """
        logger.info(f"Chunking document: {document.name} (size={self.chunk_size}, overlap={self.chunk_overlap})")
        
        chunks = []
        text = document.content
        text_length = len(text)
        
        if text_length == 0:
            logger.warning(f"Document {document.name} has no content to chunk.")
            return chunks
        
        start = 0
        chunk_index = 1
        
        while start < text_length:
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Format: sample.txt_chunk_0001
            chunk_id = f"{document.name}_chunk_{chunk_index:04d}"
            
            # For TXT/DOCX we use page 1 as default. 
            # PDF could map text to pages in a future iteration.
            metadata = ChunkMetadata(
                start_position=start,
                end_position=min(end, text_length),
                length=len(chunk_text)
            )
            
            chunks.append(Chunk(
                id=chunk_id, 
                page=1,
                text=chunk_text, 
                metadata=metadata
            ))
            
            chunk_index += 1
            # Advance start by the chunk size minus the overlap
            start += (self.chunk_size - self.chunk_overlap)
            
        return chunks
