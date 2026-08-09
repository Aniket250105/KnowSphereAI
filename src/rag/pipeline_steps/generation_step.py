import time
from typing import Dict, Any, List
from src.llm.llm_service import LLMService
from src.prompts.prompt_factory import PromptFactory
from src.routing.query_classifier import QueryClassifier

class GenerationStep:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        
    def execute(self, query: str, context_string: str, history_str: str, unique_sources: List[Dict[str, Any]]) -> dict:
        """
        Generates the answer using the LLM.
        """
        query_type = QueryClassifier.classify(query)
        prompt = PromptFactory.get_prompt(query_type, question=query, context=context_string, history=history_str)
        
        start_gen = time.time()
        answer = self.llm_service.generate_response(prompt)
        generation_time = time.time() - start_gen
        
        # Append Citations to Answer
        if unique_sources:
            citation_block = "\n\nSources:\n"
            for i, src in enumerate(unique_sources, 1):
                citation_block += f"{i}. {src['document']}\n"
                citation_block += f"   Page: {src['page']}\n"
                citation_block += f"   Score: {src['score']}\n"
            answer += citation_block
            
        return {
            "answer": answer,
            "generation_time": generation_time
        }
