import time
from src.core.logger import get_logger
from src.services.retrieval_service import RetrievalService
from src.llm.llm_service import LLMService
from src.memory.conversation_memory import ConversationMemory
from src.models.rag_response import RAGResponse
from src.evaluation.evaluator import Evaluator
from src.evaluation.metrics import RAGMetrics
from datetime import datetime, timezone
from src.recommendation.question_generator import QuestionGenerator

# Import Pipeline Steps
from src.rag.pipeline_steps.retrieval_step import RetrievalStep
from src.rag.pipeline_steps.compression_step import CompressionStep
from src.rag.pipeline_steps.generation_step import GenerationStep
from src.rag.pipeline_steps.validation_step import ValidationStep

logger = get_logger(__name__)

class RAGService:
    """
    Coordinates Retrieval and Generation using orchestrated Pipeline Steps.
    """
    def __init__(self, retrieval_service: RetrievalService, llm_service: LLMService):
        self.llm_service = llm_service
        self.retrieval_step = RetrievalStep(retrieval_service)
        self.compression_step = CompressionStep()
        self.generation_step = GenerationStep(llm_service)
        self.validation_step = ValidationStep()
        
    def ask(self, query: str, memory: ConversationMemory = None) -> RAGResponse:
        logger.info(f"RAG Service processing query: '{query}'")
        start_total = time.time()
        history_str = memory.get_formatted_history() if memory else ""
        
        # 1. Retrieval Step (Includes Retries)
        start_retrieval = time.time()
        retrieval_result = self.retrieval_step.execute(query)
        search_response = retrieval_result["search_response"]
        retrieval_time = time.time() - start_retrieval
        
        if not search_response or not search_response.results:
            logger.warning("No context retrieved for the query.")
            return RAGResponse(
                answer="I couldn't find this information in the indexed documents.",
                sources=[],
                retrieved_chunks=[],
                generation_time_seconds=0.0,
                total_time_seconds=time.time() - start_total,
                confidence="LOW"
            )
            
        # 2. Compression & Ranking Step
        compression_result = self.compression_step.execute(search_response)
        compressed_response = compression_result["compressed_response"]
        context_string = compression_result["context_string"]
        metrics = compression_result["metrics"]
        
        # Extract unique sources for generation step citation block
        seen_docs = set()
        unique_sources = []
        for res in compressed_response.results:
            pos = f"{res.metadata.get('start_position', 0)}-{res.metadata.get('end_position', 0)}"
            sig = (res.document_name, res.chunk_id)
            if sig not in seen_docs:
                unique_sources.append({
                    "document": res.document_name,
                    "page": res.page,
                    "chunk_id": res.chunk_id,
                    "score": round(res.score, 4),
                    "position": pos
                })
                seen_docs.add(sig)
                
        # 3. Generation Step
        gen_result = self.generation_step.execute(query, context_string, history_str, unique_sources)
        answer = gen_result["answer"]
        generation_time = gen_result["generation_time"]
        total_time = time.time() - start_total
        
        # 4. Assemble Initial Response
        retrieved_chunks = [res.text for res in compressed_response.results]
        suggested_questions = QuestionGenerator.generate_questions(answer, unique_sources)
        
        response = RAGResponse(
            answer=answer,
            sources=unique_sources,
            retrieved_chunks=retrieved_chunks,
            generation_time_seconds=generation_time,
            total_time_seconds=total_time,
            confidence=retrieval_result["confidence"],
            suggested_questions=suggested_questions,
            compressed_chunks=metrics["compressed_chunks"],
            original_chunks=metrics["original_chunks"],
            compression_ratio=metrics["compression_ratio"],
            retry_count=retrieval_result["retry_count"],
            expanded_query=retrieval_result["expanded_query"]
        )
        
        # 5. Validation Step
        self.validation_step.execute(answer, retrieved_chunks, unique_sources, response)
        
        # Extract flat metrics for backward compatibility with Analytics
        # If grounding fails terribly, we might want to log it
        Evaluator.log_metrics(RAGMetrics(
            query=query,
            retrieval_time_seconds=retrieval_time,
            embedding_time_seconds=0.0,
            generation_time_seconds=generation_time,
            total_time_seconds=total_time,
            timestamp=datetime.now(timezone.utc)
        ))
        
        return response
        
    def ask_stream(self, query: str, memory: ConversationMemory = None):
        logger.info(f"RAG Service streaming query: '{query}'")
        start_total = time.time()
        history_str = memory.get_formatted_history() if memory else ""
        
        # 1. Retrieval
        start_retrieval = time.time()
        retrieval_result = self.retrieval_step.execute(query)
        search_response = retrieval_result["search_response"]
        
        from src.models.stream_response import StreamEvent
        
        if not search_response or not search_response.results:
            yield StreamEvent(type="token", content="I couldn't find this information in the indexed documents.")
            yield StreamEvent(type="metadata", metadata={
                "confidence": "LOW",
                "sources": [],
                "suggestions": []
            })
            return
            
        # 2. Compression & Ranking
        compression_result = self.compression_step.execute(search_response)
        compressed_response = compression_result["compressed_response"]
        context_string = compression_result["context_string"]
        metrics = compression_result["metrics"]
        
        seen_docs = set()
        unique_sources = []
        for res in compressed_response.results:
            pos = f"{res.metadata.get('start_position', 0)}-{res.metadata.get('end_position', 0)}"
            sig = (res.document_name, res.chunk_id)
            if sig not in seen_docs:
                unique_sources.append({
                    "document": res.document_name,
                    "page": res.page,
                    "chunk_id": res.chunk_id,
                    "score": round(res.score, 4),
                    "position": pos
                })
                seen_docs.add(sig)
                
        # 3. Generation (Stream)
        from src.routing.query_classifier import QueryClassifier
        from src.prompts.prompt_factory import PromptFactory
        query_type = QueryClassifier.classify(query)
        prompt = PromptFactory.get_prompt(query_type, question=query, context=context_string, history=history_str)
        
        start_gen = time.time()
        answer_chunks = []
        try:
            for token in self.llm_service.llm.generate_stream(prompt):
                answer_chunks.append(token)
                yield StreamEvent(type="token", content=token)
        except Exception as e:
            logger.error(f"Stream generation failed: {e}")
            yield StreamEvent(type="error", content=f"Stream generation failed: {e}")
            return
            
        full_answer = "".join(answer_chunks)
        generation_time = time.time() - start_gen
        
        # 4. Assemble Citations
        if query_type.name != "GENERAL_CHAT" and unique_sources:
            citation_block = "\n\nSources:\n"
            for i, src in enumerate(unique_sources, 1):
                citation_block += f"{i}. {src['document']}\n"
                citation_block += f"   Page: {src['page']}\n"
                citation_block += f"   Score: {src['score']}\n"
                
            yield StreamEvent(type="token", content=citation_block)
            full_answer += citation_block
        
        total_time = time.time() - start_total
        
        # 5. Validation (Post-stream)
        response_obj = RAGResponse(
            answer=full_answer,
            sources=unique_sources,
            retrieved_chunks=[res.text for res in compressed_response.results],
            generation_time_seconds=generation_time,
            total_time_seconds=total_time,
            confidence=retrieval_result["confidence"],
            suggested_questions=QuestionGenerator.generate_questions(full_answer, unique_sources),
            compressed_chunks=metrics["compressed_chunks"],
            original_chunks=metrics["original_chunks"],
            compression_ratio=metrics["compression_ratio"],
            retry_count=retrieval_result["retry_count"],
            expanded_query=retrieval_result["expanded_query"]
        )
        
        self.validation_step.execute(full_answer, response_obj.retrieved_chunks, unique_sources, response_obj)
        
        yield StreamEvent(type="metadata", metadata={
            "confidence": retrieval_result["confidence"],
            "sources": unique_sources,
            "suggestions": response_obj.suggested_questions,
            "timings": {
                "generation_time_seconds": generation_time,
                "total_time_seconds": total_time
            },
            # Return verification/hallucination status as metadata to UI if it wants it
            "evaluation": {
                "grounding_score": response_obj.evaluation.grounding.score if response_obj.evaluation and response_obj.evaluation.grounding else 0.0,
                "hallucination_risk": response_obj.evaluation.hallucination.risk if response_obj.evaluation and response_obj.evaluation.hallucination else "UNKNOWN"
            }
        })
