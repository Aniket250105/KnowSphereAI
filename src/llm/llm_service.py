from src.core.logger import get_logger
from src.llm.base_llm import BaseLLM
from src.llm.huggingface_llm import HuggingFaceLLM

logger = get_logger(__name__)

class LLMService:
    """
    Orchestrator for text generation. 
    Hides the concrete implementation of the language model from the rest of the application.
    """
    
    def __init__(self, llm: BaseLLM = None):
        # Default to HuggingFace implementation if none provided via DI
        self.llm = llm if llm else HuggingFaceLLM()
        
    def generate_response(self, prompt: str) -> str:
        """
        Generates text given a prompt string.
        """
        logger.info("Generating response via LLM...")
        try:
            return self.llm.generate(prompt)
        except Exception as e:
            logger.error(f"LLMService failed to generate response: {e}")
            raise
            
    def warmup(self):
        """Forces the LLM to load into memory."""
        self.llm.load_model()
