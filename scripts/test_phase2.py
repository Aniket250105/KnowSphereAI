import sys
import json
import time
from pathlib import Path

# Add the project root to sys.path so we can import src modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core import config
from src.document_processing.processor import DocumentProcessor
from src.core.logger import get_logger

logger = get_logger(__name__)

def create_sample_files(raw_dir: Path) -> dict:
    """Creates sample files for testing."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    txt_path = raw_dir / "sample.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        # Include extra spaces and blank lines to test cleaner
        text = "This is a sample text document.      \n\n\n\nIt has excessive blank lines.\n\tAnd some tabs."
        # Make it long enough to trigger chunking
        text += " " + ("Repeating content to increase length. " * 20)
        f.write(text)
        
    return {
        "txt": txt_path
    }

def main():
    raw_dir = config.RAW_DIR
    processed_dir = config.PROCESSED_DIR
    
    print("Setting up sample files...")
    samples = create_sample_files(raw_dir)
    
    print("\nInitializing DocumentProcessor...")
    processor = DocumentProcessor()
    
    for file_type, file_path in samples.items():
        print(f"\n=========================================")
        print(f" Processing {file_type.upper()} File")
        print(f"=========================================\n")
        
        start_time = time.time()
        try:
            processed_doc = processor.process(file_path)
            end_time = time.time()
            processing_time = end_time - start_time
            
            doc_meta = processed_doc.document
            
            print(f"Document ID     : {doc_meta.id}")
            print(f"Document Name   : {doc_meta.name}")
            print(f"Characters      : {doc_meta.characters}")
            print(f"Pages           : {doc_meta.pages}")
            print(f"Chunks          : {doc_meta.chunk_count}")
            print(f"Processing Time : {processing_time:.4f} seconds")
            
            json_path = processed_dir / f"{doc_meta.name}.json"
            print(f"Output File     : {json_path}")
            
            print("\n--- Running Validations ---")
            
            # Validation 1: JSON exists
            assert json_path.exists(), "Output JSON file does not exist."
            print("[OK] JSON exists")
            
            # Validation 2: JSON parses correctly
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("[OK] JSON parses correctly")
            
            # Validation 3: document section exists
            assert "document" in data, "'document' key missing from JSON"
            print("[OK] document section exists")
            
            # Validation 4: chunks exist
            assert "chunks" in data, "'chunks' key missing from JSON"
            assert isinstance(data["chunks"], list), "'chunks' should be a list"
            print("[OK] chunks exist")
            
            # Validation 5: metadata is complete
            expected_keys = [
                "id", "name", "type", "path", "pages", "characters", 
                "language", "encoding", "created_at", "modified_at", 
                "processed_at", "chunk_count", "chunk_size", "chunk_overlap", "version"
            ]
            doc_dict = data["document"]
            for key in expected_keys:
                assert key in doc_dict, f"Missing key '{key}' in document metadata"
            print("[OK] metadata is complete")
            
            print("\nSUCCESS: End-to-End Pipeline test passed.")
                
        except Exception as e:
            print(f"\nERROR: Test failed during {file_type.upper()} processing or validation:")
            print(e)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
