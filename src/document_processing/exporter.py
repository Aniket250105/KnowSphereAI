import json
import dataclasses
from pathlib import Path
from typing import Any, Dict

from src.core.logger import get_logger
from src.models.document import ProcessedDocument

logger = get_logger(__name__)

class JSONExporter:
    """
    Exports a ProcessedDocument to a structured JSON file.
    """
    
    def __init__(self, output_dir: Path | str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export(self, processed_doc: ProcessedDocument) -> Path:
        """
        Saves the processed document as a JSON file in the output directory and validates it.
        
        Args:
            processed_doc (ProcessedDocument): The document to export.
            
        Returns:
            Path: The path to the saved JSON file.
        """
        file_name = f"{processed_doc.document.name}.json"
        output_path = self.output_dir / file_name
        
        # dataclasses.asdict converts the dataclass tree into a dictionary
        export_data = dataclasses.asdict(processed_doc)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)
            
        self._validate_export(output_path, processed_doc)
            
        return output_path

    def _validate_export(self, json_path: Path, processed_doc: ProcessedDocument):
        """
        Validates the exported JSON file against expected constraints.
        
        Args:
            json_path (Path): Path to the generated JSON file.
            processed_doc (ProcessedDocument): The original processed document.
            
        Raises:
            ValueError: If validation fails.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON validation failed: Invalid JSON format. {e}")
            
        if "document" not in data or "chunks" not in data:
            raise ValueError("JSON validation failed: Missing required 'document' or 'chunks' keys.")
            
        if len(data["chunks"]) != data["document"]["chunk_count"]:
            raise ValueError(
                f"JSON validation failed: 'chunk_count' ({data['document']['chunk_count']}) "
                f"does not match actual number of chunks ({len(data['chunks'])})."
            )
            
        if data["document"]["characters"] != processed_doc.document.characters:
            raise ValueError("JSON validation failed: Character count mismatch.")
            
        logger.info(f"JSON validation passed successfully for {json_path.name}.")
