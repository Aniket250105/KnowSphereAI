# Phase 6: Enterprise Analytics Architecture (Phase 6C Extension)

## Overview
Phase 6C adds an enterprise-grade observability and administration layer, monitoring the knowledge base usage, system health, and RAG pipeline performance. 

## Architectural Constraints
- **Observer Pattern**: The analytics layer strictly observes interactions at the API layer. The core internal RAG logic (`src/rag/`, `src/llm/`, `src/embeddings/`, etc.) remains 100% unmodified.
- **Dependency Injection**: Dependencies are fetched from `dependencies.py` and passed into routing endpoints.
- **SQLite Persistence**: Analytics models append to the local relational database without mutating existing core structures (e.g., `documents`, `messages`).

## Database Schema Extensions
The following models were introduced:
- `AnalyticsEventModel`: Captures granular query telemetry including query text, confidence score, generation latency, and retrieval latency.
- `DocumentAnalyticsModel`: Tracks document-level metrics such as retrieval counts, last access timestamps, and aggregate similarity performance.
- `UserAnalyticsModel`: Captures high-level usage per session (total queries, session duration).
- `FeedbackAnalyticsModel`: A global singleton aggregating helpful vs. unhelpful responses.

## Metrics Collection Flow
1. **User Query**: A user submits a query to `/chat` or `/chat/stream`.
2. **RAG Pipeline**: The unchanged pipeline processes the query, performs Hybrid Search, generates a response, and formats the metadata.
3. **API Interceptor**: Inside `src/api/routes.py`, the response object (or trailing stream metadata event) is intercepted. 
4. **Analytics Service**: The API routes dispatch the metadata asynchronously (or sequentially) to `AnalyticsService.record_query(...)`.
5. **Persistence**: The SQLite database commits the new entries securely via SQLAlchemy.

## Admin Dashboard Architecture
- **API (`src/api/admin_routes.py`)**: Exposes REST interfaces like `/admin/analytics/system` and `/admin/analytics/documents`.
- **UI (`src/ui/admin_dashboard.py`)**: Provides a `gr.Blocks()` based modular UI communicating purely with the Admin APIs, maintaining separation of frontend state and backend logic.
- **Integration**: Nested as a new tab ("Admin Dashboard") into `src/ui/gradio_app.py`.

## Automated Reporting
A background mechanism (`src/analytics/report_generator.py`) generates system-wide performance snapshots and exports them to the `reports/` folder. This is callable via the Admin UI.

## Future Scalability
- The analytics models can be abstracted behind an interface to allow for future migration from SQLite to specialized TSDBs (Time-Series Databases like InfluxDB) or telemetry systems (Datadog/OpenTelemetry).
- Streaming and event handling could be decoupled further into an event bus (e.g., Redis Pub/Sub, Kafka) ensuring high throughput logging without degrading RAG latency.
