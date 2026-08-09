from abc import ABC, abstractmethod

class BaseLLM(ABC):
    """
    Abstract base class for all Language Models.
    Allows swapping between HuggingFace, OpenAI, Llama.cpp, etc.
    """
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate text from the provided prompt.
        """
        pass
        
    @abstractmethod
    def generate_stream(self, prompt: str):
        """
        Generate text progressively (streaming).
        """
        pass
        
    @abstractmethod
    def load_model(self):
        """
        Load the model into memory.
        """
        pass
        
    @abstractmethod
    def get_model_info(self) -> dict:
        """
        Return metadata about the loaded model.
        """
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the model is loaded and ready.
        """
        pass
