# Phase 3 – Retrieval Engine Architecture Design (Revised)

## 1. System Architecture
The Phase 3 retrieval engine establishes a highly modular, decoupled bridge between processed documents and semantic search, strictly adhering to SOLID principles and clean architecture.

- **Embedding Layer (`src/embeddings/`)**: Handles the conversion of text into dense vectors. Implements the `BaseEmbeddingModel` abstract interface.
- **Vector Database Abstraction (`src/vectorstore/`)**: Provides an interface for vector indexing (`BaseVectorStore`), ensuring the application isn't tightly coupled to Qdrant.
- **Collection Manager (`src/vectorstore/collection_manager.py`)**: Dedicated strictly to vector store lifecycle events (creation, deletion, counting), decoupling DDL operations from CRUD operations.
- **Application Services (`src/services/`)**: Orchestrates the workflows via Dependency Injection (DI) by coordinating models, embeddings, and vector stores. Included are `IndexingService`, `RetrievalService`, and `HealthService`.

## 2. Workflows
### 2.1 Embedding Workflow
- `BaseEmbeddingModel` defines the strict contract (`embed_text`, `embed_batch`, `get_dimension`).
- `EmbeddingModel` implements the contract as a thread-safe Singleton that lazily loads the Sentence Transformers model.
- `EmbeddingService` exposes clean endpoints to the application, preventing raw model instantiation inside business logic.

### 2.2 Vector Indexing Workflow (IndexingService)
1. **Load**: Parses the `ProcessedDocument` JSON file.
2. **Duplicate Check**: Executes a query with a metadata filter on `document_id`. If matches are found, it safely aborts indexing.
3. **Embed**: Batches text chunks and passes them to the `EmbeddingService`.
4. **Map**: Combines vectors, deep tracking metadata (including `document_hash`, `document_path`, and positional data), into strict `VectorPoint` dataclasses.
5. **Upsert**: Pushes `VectorPoint` arrays into Qdrant via the abstract interface.

### 2.3 Semantic Retrieval Workflow (RetrievalService)
1. **Query Prep**: The user's string query is embedded into a vector.
2. **Search**: The vector is passed to the Qdrant store which performs a Cosine similarity search (with optional metadata filters).
3. **Hydration**: Raw hits are mapped to typed `SearchResult` objects.
4. **Response**: A compiled `SearchResponse` is returned containing fine-grained latency metrics (`search_time_seconds`, `embedding_time_seconds`, `retrieval_time_seconds`) and the top K hits.

## 3. Technology Choices
- **Sentence Transformers (BAAI/bge-small-en-v1.5)**: Chosen for its exceptional balance between performance (high MTEB benchmarks) and CPU efficiency.
- **Qdrant**: High-performance local vector database built in Rust, chosen because it doesn't require complex Docker networking for standalone implementations.
- **Cosine Similarity**: Measures the angle between vectors, prioritizing the semantic direction ("meaning") over magnitude ("length").

## 4. Future Readiness (RAG & Llama Integration)
- **Dependency Injection**: Services accept abstract implementations, making it trivial to swap out the embedding model or vector database in the future.
- **Context Expansion**: Retaining `start_position` and `end_position` enables LLMs to intelligently widen their context window when a single retrieved chunk isn't sufficient.
- **Metadata Filtering**: The system fully supports searching by specific metadata filters (e.g., retrieving only chunks from `document_type: pdf`).
- **Clean Contracts**: Because the retrieval service strictly returns structured data, integrating Llama in Phase 4 is as simple as injecting the `SearchResponse.results` text into a prompt template, without rewriting any Phase 3 logic.

## 5. Retrieval Evaluation (Phase 3.5)

To ensure the foundational retrieval engine is solid before integrating an LLM, a rigorous evaluation layer was implemented.

### Dataset
- **Number of documents**: 4 diverse domain-specific files (`university_rules.txt`, `python_basics.txt`, `operating_systems.txt`, `machine_learning.txt`).
- **Number of queries**: 10 distinct queries, categorized by domain and difficulty (easy, medium, hard).

### Metrics Assessed
- **Top-1 Accuracy**: Percentage of queries where the single best result is the correct document.
- **Top-3 Accuracy**: Percentage of queries where the correct document appears in the top 3 results.
- **Mean Reciprocal Rank (MRR)**: Average of the reciprocal ranks of the first correct hit. (e.g. 1st = 1.0, 2nd = 0.5, 3rd = 0.33).
- **Recall@K**: Did the correct document appear anywhere in the first K results? (Implemented for K=3).

### Results Summary
- **Queries Tested**: 10
- **Top-1 Accuracy**: 100.0%
- **Top-3 Accuracy**: 100.0%
- **MRR**: 1.0000
- **Recall@3**: 100.0%

### Duplicate Prevention Strategy
To ensure the vector index remains pristine, `IndexingService` employs a robust duplicate validation mechanism. 
Before extracting embeddings and upserting, the service queries Qdrant using the `document_id` metadata filter. 
If the document already exists in the collection, the pipeline gracefully aborts, preventing ID clashes or redundant vector saturation. This is enforced by `tests/test_duplicate_indexing.py`.

### Limitations
- **Small Benchmark Dataset**: Currently evaluated against only 10 handcrafted queries.
- **Domain-Specific Documents**: The system may perform differently on unstructured or vastly disparate out-of-domain knowledge.
