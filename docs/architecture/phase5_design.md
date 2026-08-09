# Phase 5 Design: Application Layer

## Overview
Phase 5 implements the application layer for KnowSphere AI, following a decoupled architecture where the FastAPI backend handles the heavy lifting, and an independent Gradio frontend provides the user interface.

## Application Architecture

The system is now structured into two main layers that communicate via HTTP:

1.  **FastAPI Backend (`src/api`)**:
    *   Exposes endpoints for health checks, document uploads, and chat.
    *   Injects the existing core abstractions (`DocumentProcessor`, `IndexingService`, `RAGPipeline`) as singletons using FastAPI's `Depends()`.
    *   Manages stateless HTTP requests, maintaining conversational state via a generated `session_id`.

2.  **Gradio Frontend (`src/ui`)**:
    *   A web-based user interface providing document upload capabilities and a conversational chatbot interface.
    *   Runs independently and connects to the backend through a lightweight API client (`src/ui/api_client.py`).
    *   Generates and stores a unique UUID session ID per browser tab to ensure isolated conversational context.

## API Flow

### GET `/api/v1/health`
Returns the status of the API, the vector database, the embedding model, and the LLM service.

### POST `/api/v1/upload`
1. Receives an `UploadFile` stream (PDF, DOCX, TXT).
2. Writes the stream to `data/raw/`.
3. Triggers the existing `DocumentProcessor` pipeline to clean, chunk, and export JSON.
4. Triggers the existing `IndexingService` to embed the chunks and upsert to Qdrant.
5. Returns a status indicating completion alongside the chunk count.

### POST `/api/v1/chat`
1. Receives a `ChatRequest` containing a query and a `session_id`.
2. Triggers `RAGPipeline.ask()`. The pipeline fetches the user's isolated `ConversationMemory` using `SessionManager`.
3. Performs semantic retrieval from Qdrant, builds a context-aware prompt, and generates an LLM response.
4. Returns a `ChatResponse` containing the answer, precise citations (source document and page), and performance timings.

## Session Management
Session management prevents data leakage between users:
*   The UI assigns a UUID (`session_id`) to every user visiting the Gradio page.
*   All `/chat` POST requests pass this `session_id`.
*   The `SessionManager` in `src/memory/session_manager.py` fetches the in-memory chat history associated with that specific UUID.

## Deployment Strategy
To guarantee a repeatable build environment and simplified setup, the application has been Dockerized. 

The `Dockerfile` builds a Python 3.10 slim image, installing dependencies and copying the necessary codebase. `docker-compose.yml` mounts the `data/` volume dynamically to persist Qdrant indices and processed JSONs across container restarts.

## Future Outlook (React/Mobile Migration)
The decoupled nature of this architecture ensures that substituting Gradio with a React (Next.js) or a mobile (React Native/Flutter) application requires exactly **zero** backend changes. Future frontends merely need to replicate the HTTP requests defined in `api_client.py`.
