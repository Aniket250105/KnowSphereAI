import json
import os
import sys
import time
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.embeddings.embedding_service import EmbeddingService
from src.vectorstore.qdrant_store import QdrantVectorStore
from src.services.retrieval_service import RetrievalService
from src.llm.llm_service import LLMService
from src.services.rag_service import RAGService

def run_evaluation():
    print("Starting Phase 8A Evaluation...")
    
    # Initialize Services
    vector_store = QdrantVectorStore()
    embedding_service = EmbeddingService()
    retrieval_service = RetrievalService(vector_store, embedding_service)
    llm_service = LLMService()
    
    rag_service = RAGService(retrieval_service, llm_service)
    
    # Load Benchmark Dataset
    benchmark_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'evaluation', 'phase8_questions.json')
    if not os.path.exists(benchmark_path):
        print(f"Benchmark file not found at {benchmark_path}")
        return
        
    with open(benchmark_path, 'r') as f:
        questions = json.load(f)
        
    metrics = {
        "queries": 0,
        "total_latency": 0.0,
        "total_grounding_score": 0.0,
        "total_retries": 0,
        "total_compression_ratio": 0.0,
        "total_hallucinations": 0,
        "total_citation_warnings": 0,
        "total_original_chunks": 0,
        "total_compressed_chunks": 0
    }
    
    for q in questions:
        query = q["query"]
        print(f"\nEvaluating Query: '{query}'")
        
        response = rag_service.ask(query, memory=None)
        
        metrics["queries"] += 1
        metrics["total_latency"] += response.total_time_seconds
        metrics["total_retries"] += response.retry_count
        metrics["total_compression_ratio"] += response.compression_ratio
        metrics["total_original_chunks"] += response.original_chunks
        metrics["total_compressed_chunks"] += response.compressed_chunks
        
        if response.evaluation:
            if response.evaluation.grounding:
                metrics["total_grounding_score"] += response.evaluation.grounding.score
                print(f"  Grounding Score: {response.evaluation.grounding.score} ({response.evaluation.grounding.level})")
                
            if response.evaluation.hallucination:
                if response.evaluation.hallucination.risk in ["MEDIUM", "HIGH"]:
                    metrics["total_hallucinations"] += 1
                print(f"  Hallucination Risk: {response.evaluation.hallucination.risk}")
                
            if response.evaluation.citation_validation:
                metrics["total_citation_warnings"] += len(response.evaluation.citation_validation.warnings)
                print(f"  Citation Warnings: {len(response.evaluation.citation_validation.warnings)}")
        
        print(f"  Latency: {response.total_time_seconds:.2f}s | Retries: {response.retry_count}")
        print(f"  Compression: {response.original_chunks} -> {response.compressed_chunks} chunks")

    print("\n" + "="*50)
    print("PHASE 8A EVALUATION RESULTS")
    print("="*50)
    
    q_count = metrics["queries"]
    if q_count > 0:
        print(f"Total Queries: {q_count}")
        print(f"Average Latency: {metrics['total_latency'] / q_count:.2f} seconds")
        print(f"Average Grounding Score: {metrics['total_grounding_score'] / q_count:.2f}")
        print(f"Average Retry Rate: {metrics['total_retries'] / q_count:.2f} retries per query")
        print(f"Average Compression Ratio: {metrics['total_compression_ratio'] / q_count:.2f}")
        print(f"Hallucination Rate: {(metrics['total_hallucinations'] / q_count) * 100:.1f}%")
        print(f"Average Context Length (Chunks): {metrics['total_compressed_chunks'] / q_count:.1f}")
        print(f"Total Citation Warnings: {metrics['total_citation_warnings']}")
    else:
        print("No queries evaluated.")

if __name__ == "__main__":
    run_evaluation()
