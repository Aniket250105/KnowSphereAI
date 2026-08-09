import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rag_pipeline import RAGPipeline
from src.core.logger import get_logger

logger = get_logger(__name__)

def test_rag():
    print("Initializing RAG Pipeline (This will download and load the LLM)...")
    pipeline = RAGPipeline()
    
    questions = [
        "What is artificial intelligence?",
        "What is deadlock?",
        "What is attendance policy?"
    ]
    
    print("\n=================================")
    print("KNOWSPHERE AI RAG TEST")
    print("=================================\n")
    
    for q in questions:
        print(f"Query: {q}")
        print("-" * 50)
        
        response = pipeline.ask(q)
        
        print(f"Retrieved Documents: {len(response.retrieved_chunks)}")
        print(f"Generated Answer:\n{response.answer}\n")
        
        print("Sources:")
        for source in response.sources:
            print(f"- {source['document']} (Page {source['page']}, Chunk: {source['chunk_id']}, Score: {source['score']})")
            
        print(f"\nRetrieval Time:  {response.total_time_seconds - response.generation_time_seconds:.4f}s")
        print(f"Generation Time: {response.generation_time_seconds:.4f}s")
        print("=================================\n")

if __name__ == "__main__":
    test_rag()
