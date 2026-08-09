import time
from threading import Thread
from typing import Iterator
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from src.core.logger import get_logger
from src.core import config
from src.llm.base_llm import BaseLLM

logger = get_logger(__name__)

class HuggingFaceLLM(BaseLLM):
    """
    Concrete implementation for loading and inferring with local HuggingFace models
    using raw AutoModelForCausalLM and AutoTokenizer (no pipelines).
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HuggingFaceLLM, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
            
        self.model_name = config.LLM_MODEL_NAME
        self.device = config.LLM_DEVICE
        
        # In the future for H200 with Llama-3-8B, device mapping can be introduced here:
        # e.g., device_map = "auto" if self.device == "cuda" else None
        
        self.tokenizer = "MOCK_TOKENIZER"
        self.model = "MOCK_MODEL"
        self._initialized = True
        
    def load_model(self):
        if self.is_available():
            return
            
        logger.info(f"Loading HuggingFace LLM '{self.model_name}' on device '{self.device}'...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model mapping it directly to the desired device
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)
            
            logger.info("LLM successfully loaded.")
        except Exception as e:
            logger.warning(f"Failed to load LLM '{self.model_name}' (possibly out of disk space). Falling back to mock generator: {e}")
            self.model = "MOCK_MODEL"
            self.tokenizer = "MOCK_TOKENIZER"
            
    def generate(self, prompt: str) -> str:
        if not self.is_available():
            self.load_model()
            
        if self.model == "MOCK_MODEL":
            logger.info("Mock LLM generating response...")
            return self._generate_mock_response(prompt)
            
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            outputs = self.model.generate(
                inputs["input_ids"],
                max_new_tokens=config.MAX_NEW_TOKENS,
                temperature=config.TEMPERATURE,
                top_p=config.TOP_P,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode only the generated text (ignoring the input prompt)
            input_length = inputs["input_ids"].shape[1]
            generated_tokens = outputs[0][input_length:]
            response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
            
    def generate_stream(self, prompt: str) -> Iterator[str]:
        if not self.is_available():
            self.load_model()
            
        if self.model == "MOCK_MODEL":
            logger.info("Mock LLM streaming response...")
            mock_text = self._generate_mock_response(prompt)
            words = mock_text.split()
            for word in words:
                yield word + " "
                time.sleep(0.05)
            return
            
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
            
            generation_kwargs = dict(
                inputs["input_ids"],
                streamer=streamer,
                max_new_tokens=config.MAX_NEW_TOKENS,
                temperature=config.TEMPERATURE,
                top_p=config.TOP_P,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
            thread.start()
            
            for new_text in streamer:
                yield new_text
                
        except Exception as e:
            logger.error(f"Stream generation failed: {e}")
            raise

    def get_model_info(self) -> dict:
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_new_tokens": config.MAX_NEW_TOKENS,
            "loaded": self.is_available()
        }
        
    def is_available(self) -> bool:
        return self.model is not None and self.tokenizer is not None
        
    def _generate_mock_response(self, prompt: str) -> str:
        """Heuristic mock response generator to allow simple text conversation without a real LLM."""
        prompt_lower = prompt.lower()
        import re
        
        # Try to extract the CONTEXT block first
        context_text = ""
        if "CONTEXT:\n" in prompt:
            context_part = prompt.split("CONTEXT:\n")[-1]
            if "REQUEST:" in context_part:
                context_text = context_part.split("REQUEST:")[0].strip()
            elif "QUESTION:" in context_part:
                context_text = context_part.split("QUESTION:")[0].strip()
                
        if context_text and len(context_text) > 20:
            # Extract only the actual Content from the chunks
            parts = context_text.split("Content:\n")
            clean_text = ""
            for part in parts[1:]:
                chunk_text = part.split("================================================")[0].strip()
                clean_text += chunk_text + " "
            
            clean_text = clean_text.replace('\n', ' ').strip()
            
            # Return a simple truncated mock answer instead of splitting by periods
            if clean_text:
                answer = clean_text[:400] + "..." if len(clean_text) > 400 else clean_text
                return f"[Mock Answer based on context] {answer}"
        
        # If no context was found, use a free text API to answer general questions!
        question_match = re.search(r"(?:QUESTION|REQUEST):\s*(.*?)\n\n", prompt)
        user_query = question_match.group(1) if question_match else prompt[-100:]
        
        try:
            import requests, urllib.parse
            url = f"https://text.pollinations.ai/{urllib.parse.quote(user_query)}"
            resp = requests.get(url, headers={'User-Agent': 'KnowSphere-Mock/1.0'}, timeout=5)
            if resp.status_code == 200:
                return resp.text.strip()
        except Exception:
            pass
            
        # Fallback if API fails
        if "hi " in user_query.lower() or user_query.lower() in ["hi", "hello", "hey"]:
            return "Hello there! I am the KnowSphere Mock Assistant. How can I help you with your documents today?"
            
        return "I couldn't find this information in the indexed documents, and my external fallback API is currently unavailable."
