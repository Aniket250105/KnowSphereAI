import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, Any, List
from pathlib import Path

def generate_document_id(filepath: Path) -> str:
    """Generates a stable unique ID based on filename, size, and modified time."""
    try:
        stat = filepath.stat()
        size = stat.st_size
        mtime = stat.st_mtime
    except Exception:
        size = 0
        mtime = 0
    hash_input = f"{filepath.name}_{size}_{mtime}".encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()

@dataclass
class ChunkMetadata:
    """Metadata specifically for a chunk."""
    start_position: int
    end_position: int
    length: int

@dataclass
class Chunk:
    """
    Represents a chunk of text extracted from a document.
    """
    id: str
    page: int
    text: str
    metadata: ChunkMetadata

@dataclass
class DocumentMetadata:
    """
    Comprehensive metadata for the entire document output.
    """
    id: str
    name: str
    type: str
    path: str
    pages: int
    characters: int
    language: str = "unknown"
    encoding: str = "utf-8"
    created_at: str = ""
    modified_at: str = ""
    processed_at: str = ""
    chunk_count: int = 0
    chunk_size: int = 0
    chunk_overlap: int = 0
    version: str = "1.0"

@dataclass
class Document:
    """
    Internal representation for a document loaded into memory before processing.
    """
    name: str
    file_type: str
    content: str
    path: str
    id: str = ""
    pages: int = 1
    characters: int = 0
    created_at: str = ""
    modified_at: str = ""

@dataclass
class ProcessedDocument:
    """
    Represents a document after being cleaned and chunked, ready for export.
    """
    document: DocumentMetadata
    chunks: List[Chunk] = field(default_factory=list)
