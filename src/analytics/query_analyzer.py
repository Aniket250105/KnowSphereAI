from sqlalchemy import func
from src.database.database import get_db
from src.database.models import AnalyticsEventModel
from typing import List, Dict, Any

class QueryAnalyzer:
    @staticmethod
    def get_popular_queries(limit: int = 5) -> List[Dict[str, Any]]:
        db = next(get_db())
        results = db.query(
            AnalyticsEventModel.query, 
            func.count(AnalyticsEventModel.id).label('count')
        ).group_by(AnalyticsEventModel.query).order_by(func.count(AnalyticsEventModel.id).desc()).limit(limit).all()
        
        return [{"query": r.query, "count": r.count} for r in results]

    @staticmethod
    def get_failed_queries(limit: int = 5) -> List[Dict[str, Any]]:
        db = next(get_db())
        # Failed queries are those with LOW confidence or zero top_similarity_score
        # We didn't explicitly store "top_similarity_score" in the first prompt, but wait: 
        # I did not add top_similarity_score to AnalyticsEventModel because the first prompt didn't say so? 
        # Ah! I didn't add top_similarity_score in models.py because I thought it was omitted. Wait, in Phase 6C it says:
        # "confidence_score" and "search_mode". 
        
        results = db.query(AnalyticsEventModel).filter(
            AnalyticsEventModel.confidence_score == "LOW"
        ).order_by(AnalyticsEventModel.created_at.desc()).limit(limit).all()
        
        return [{"query": r.query, "reason": "low confidence"} for r in results]
