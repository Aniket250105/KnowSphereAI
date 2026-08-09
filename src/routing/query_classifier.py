from enum import Enum
import re
from src.core.logger import get_logger

logger = get_logger(__name__)

class QueryType(Enum):
    FACTUAL = "FACTUAL"
    SUMMARY = "SUMMARY"
    MCQ_GENERATION = "MCQ_GENERATION"
    EXPLANATION = "EXPLANATION"
    DOCUMENT_SEARCH = "DOCUMENT_SEARCH"
    GENERAL_CHAT = "GENERAL_CHAT"

class QueryClassifier:
    """
    Lightweight rule-based classifier to determine query intent.
    """
    @staticmethod
    def classify(query: str) -> QueryType:
        q_lower = query.lower()
        
        if re.search(r'\b(explain|how|why|describe|detail)\b', q_lower):
            logger.info("Classified query as EXPLANATION")
            return QueryType.EXPLANATION
            
        if re.search(r'\b(summarize|summary|tldr|brief)\b', q_lower):
            logger.info("Classified query as SUMMARY")
            return QueryType.SUMMARY
            
        if re.search(r'\b(generate|create|make).*(question|mcq|quiz|test)\b', q_lower) or re.search(r'\b(questions|mcq)\b', q_lower):
            logger.info("Classified query as MCQ_GENERATION")
            return QueryType.MCQ_GENERATION
            
        if re.search(r'\b(find|search|document|file)\b', q_lower):
            logger.info("Classified query as DOCUMENT_SEARCH")
            return QueryType.DOCUMENT_SEARCH
            
        if re.search(r'\b(hi|hello|hey|thanks|thank you)\b', q_lower) and len(q_lower.split()) < 5:
            logger.info("Classified query as GENERAL_CHAT")
            return QueryType.GENERAL_CHAT
            
        logger.info("Classified query as FACTUAL")
        return QueryType.FACTUAL
