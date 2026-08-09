import re
from src.core.logger import get_logger
from src.models.document import Document

logger = get_logger(__name__)

class DocumentCleaner:
    """
    Cleans document text through a pipeline of specific cleaning methods.
    """
    
    def clean(self, document: Document) -> Document:
        """
        Executes the cleaning pipeline on the document's content.
        
        Args:
            document (Document): The document to clean.
            
        Returns:
            Document: The updated document with cleaned content.
        """
        logger.info(f"Cleaning document: {document.name}")
        text = document.content
        
        text = self.remove_excessive_whitespace(text)
        text = self.normalize_newlines(text)
        text = self.remove_repeated_blank_lines(text)
        
        document.content = text
        return document

    def remove_excessive_whitespace(self, text: str) -> str:
        """Replaces multiple spaces or tabs with a single space."""
        return re.sub(r'[ \t]+', ' ', text)
        
    def normalize_newlines(self, text: str) -> str:
        """Normalizes various line endings to standard Unix newlines."""
        return text.replace('\r\n', '\n').replace('\r', '\n')
        
    def remove_repeated_blank_lines(self, text: str) -> str:
        """Reduces 3 or more consecutive newlines to exactly 2."""
        return re.sub(r'\n{3,}', '\n\n', text)
