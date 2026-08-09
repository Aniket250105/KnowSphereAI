# Phase 9A: AI Agents, Tool Calling & Workflow Automation

## Overview

This phase introduces an extensible AI Agent orchestration layer to KnowSphere AI, transforming it from a traditional Retrieval-Augmented Generation (RAG) assistant into an Agent platform. It enables task planning, external tool invocation, and multi-step workflow execution while strictly preserving the existing infrastructure through a composition-based architecture.

## Architectural Design

### 1. Composition over Modification

The Agent Layer runs *on top* of the existing RAG pipeline (`src/rag/`) rather than modifying it. `KnowledgeBaseTool` injects `get_rag_pipeline()` from the main dependencies and exposes RAG functionality seamlessly to agents. Existing analytics and endpoints remain fully backward-compatible.

### 2. Core Components

The framework adopts several design patterns:

- **BaseAgent (Interface)**: Defines the contract for all agents (`plan()`, `execute()`, `run()`).
- **BaseTool (Interface)**: Defines the contract for all executable tools (`execute()`, `validate()`, `metadata`).
- **ToolRegistry (Registry Pattern)**: A central class-level registry where tools self-register or are registered upon startup.
- **KeywordPlanner (Strategy Pattern)**: A deterministic keyword-based planner determining optimal execution steps, routing specific requests to the correct tools without requiring expensive LLM planning steps for basic queries.
- **WorkflowEngine**: Orchestrates multi-step ExecutionPlans with retry and timeout capabilities, maintaining an execution trace of success/failures.
- **AgentFactory (Factory Pattern)**: Handles dynamic instantiation of `SimpleAgent`, `RAGAgent`, and `WorkflowAgent`.

### 3. Analytics Integration

Agent execution and tool invocations hook into `AgentAnalytics`, which tracks tool usage, error rates, and average agent latency, laying the groundwork for a more robust analytics observer in future iterations.

## Execution Flow

1. User submits a request via the `/api/v1/agent/chat` endpoint.
2. `AgentFactory` instantiates the designated agent.
3. The Agent generates an `ExecutionPlan` using the `KeywordPlanner`.
4. The plan is executed either immediately (SimpleAgent) or dynamically handled (WorkflowAgent).
5. All actions and timestamps are stored inside `AgentMemory`.
6. Tool outputs or RAG outcomes are returned to the user alongside metadata tracing tool execution.
