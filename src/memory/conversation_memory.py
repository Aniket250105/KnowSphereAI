from typing import List, Dict

class ConversationMemory:
    """
    Stores conversational history for context-aware generation.
    """
    def __init__(self, max_history: int = 5, initial_history: List[Dict[str, str]] = None):
        self.history: List[Dict[str, str]] = initial_history or []
        self.max_history = max_history
        self._enforce_limit()
        
    def add_user_message(self, message: str):
        self.history.append({"role": "user", "content": message})
        self._enforce_limit()
        
    def add_assistant_message(self, message: str):
        self.history.append({"role": "assistant", "content": message})
        self._enforce_limit()
        
    def get_history(self) -> List[Dict[str, str]]:
        return self.history
        
    def get_formatted_history(self) -> str:
        if not self.history:
            return "No prior conversation."
            
        formatted = []
        for msg in self.history:
            role = "User" if msg["role"] == "user" else "KnowSphere"
            formatted.append(f"{role}: {msg['content']}")
            
        return "\n".join(formatted)
        
    def clear(self):
        self.history = []
        
    def _enforce_limit(self):
        # Keeps the last N exchanges (User + Assistant = 2 items per exchange)
        limit = self.max_history * 2
        if len(self.history) > limit:
            self.history = self.history[-limit:]
