# Phase 8B: Advanced RAG Evaluation & Self-Optimization Framework

## Overview
The Evaluation Framework transforms KnowSphere AI into a self-optimizing, observable AI pipeline. 

### Core Design Principles
1. **Observer Pattern**: The framework evaluates the system by calling `RAGPipeline.ask()`. It does not inject code or mutate existing services.
2. **Zero Performance Impact**: Benchmarking code only executes via explicit `/admin/evaluation/run` requests. Production API calls incur no overhead.
3. **Reproducibility**: Datasets are versioned and configurations are snapshotted on every run.

## Components

### 1. Dataset Layer (`src/evaluation/datasets.py`)
Parses `JSON` and `CSV` files. Organizes test cases into predefined `profiles` (Quick, Standard, Full). Supports categories for deeper analysis.

### 2. Metrics Layer (`src/evaluation/metrics.py`)
Calculates:
- **Retrieval**: Recall@K, MRR, NDCG
- **Generation**: Citation Accuracy, Grounding Score, Faithfulness
- **Performance**: Latency tracking
Provides configurable weighting for deriving the `average_score`.

### 3. Orchestrator (`src/evaluation/benchmark_runner.py`)
Iterates over dataset queries, calls the `RAGService`, records latency, computes metrics, and generates a structured benchmark report. Handles **Baseline Comparisons** against prior runs.

### 4. A/B Testing (`src/evaluation/prompt_testing.py`, `retrieval_testing.py`)
Allows comparing configs head-to-head (e.g. Prompt A vs Prompt B, Dense vs Hybrid Search) to automatically generate Leaderboards.

### 5. UI and Reporting
- **Report Generator**: Writes JSON, CSV, MD, and Matplotlib charts to `reports/benchmark_<timestamp>`.
- **Gradio Dashboard**: Displays leaderboards, failure explorer (query-by-query breakdown of errors like Hallucinations and Low Recall), and historical trends.

## Schema Additions
- `EvaluationRunModel`: Stores configuration snapshots and dataset versions.
- `EvaluationResultModel`: Stores query-level performance and failure reasoning.
- `PromptExperimentModel`: Tracks A/B tests.
