from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.models.document import Document, Chunk

class BaseDocumentLoader(ABC):
    """
    Abstract base class for all document loaders.
    """
    
    @abstractmethod
    def load(self, file_path: Path) -> Document:
        """
        Reads a file from the given path and extracts its text and metadata.
        
        Args:
            file_path (Path): Path to the document.
            
        Returns:
            Document: A structured document object containing text and metadata.
        """
        pass

class BaseChunker(ABC):
    """
    Abstract base class for all text chunking strategies.
    """
    
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """
        Splits a document's content into smaller chunks.
        
        Args:
            document (Document): The document to be chunked.
            
        Returns:
            List[Chunk]: A list of chunk objects.
        """
        pass
