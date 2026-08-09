# Phase 4 Design: Retrieval-Augmented Generation (RAG) Architecture

## 1. Architectural Overview
Phase 4 layers generative language models on top of our stable Phase 3 retrieval engine. 
We introduced a strict boundary between retrieval, context building, and text generation.

### RAG Architecture Diagram
```mermaid
flowchart TD
    User([User Query]) --> RAG[RAGPipeline]
    RAG --> RAGSrv[RAGService]
    
    subgraph Phase 3 Retrieval
        RAGSrv --> RetSrv[RetrievalService]
        RetSrv --> EmbSrv[EmbeddingService]
        RetSrv --> Qdrant[(Qdrant Vector DB)]
        Qdrant --> RetSrv
        RetSrv -.-> Hits[Top K Chunks]
    end
    
    subgraph Phase 4 Generation
        Hits --> CtxBuilder[ContextBuilder]
        CtxBuilder --> PrmptBuilder[PromptTemplate]
        PrmptBuilder -.-> Prompt[Formatted Prompt]
        
        Prompt --> LLMSrv[LLMService]
        LLMSrv --> BaseLLM{BaseLLM Interface}
        BaseLLM --> HF[HuggingFaceLLM]
        HF -.-> Answer[Generated Text]
    end
    
    Answer --> RAGSrv
    RAGSrv --> Response[RAGResponse (Answer + Citations)]
    Response --> User
```

## 2. Component Data Flow
1. **User Query**: String input from UI/API.
2. **Retrieval**: `RetrievalService` fetches the closest semantic matching chunks from Qdrant via `SearchResponse`.
3. **Context Construction**: `ContextBuilder` deduplicates chunks, enforces the `MAX_CONTEXT_LENGTH`, and formats them rigidly indicating `Source`, `Page`, `Chunk`, and `Similarity`.
4. **Prompting**: `prompt_template.py` merges the System instructions, Context, and the Question.
5. **Generation**: `LLMService` utilizes the `BaseLLM` interface to execute generation, fully abstracted from the rest of the application.
6. **Response Synthesis**: `RAGService` hydrates the `RAGResponse` object, injecting explicit sources matching what the LLM used for its answer.

## 3. Why the LLM Abstraction Exists
To ensure extreme forward-compatibility, `RAGService` has zero knowledge of PyTorch, Transformers, or APIs. It only knows `BaseLLM`. 

Currently, `HuggingFaceLLM` loads a tiny quantized chat model. Tomorrow, another developer could implement `OpenAILLM(BaseLLM)` or `LlamaCppLLM(BaseLLM)` without changing a single line of RAG logic.

## 4. Hardware Migration: CPU to GPU (H200)
Currently, in development mode:
- `LLM_MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"`
- `LLM_DEVICE = "cpu"`

To migrate this to the University H200 cluster for **Llama 3 8B**:

1. **Update `src/core/config.py`**:
   ```python
   LLM_MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
   LLM_DEVICE = "cuda"
   ```

2. **(Optional) Multi-GPU Mapping**: 
   Since we utilize raw `AutoModelForCausalLM` without pipeline constraints, `device_map="auto"` can natively distribute the 8B model across VRAM efficiently.
   ```python
   # Inside HuggingFaceLLM.load_model()
   self.model = AutoModelForCausalLM.from_pretrained(
       self.model_name,
       device_map="auto",
       torch_dtype=torch.bfloat16
   )
   ```
