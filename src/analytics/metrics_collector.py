from sqlalchemy.sql import func
from src.database.database import get_db
from src.database.models import AnalyticsEventModel, DocumentAnalyticsModel, FeedbackAnalyticsModel, DocumentModel

class MetricsCollector:
    @staticmethod
    def get_system_metrics():
        db = next(get_db())
        total_queries = db.query(AnalyticsEventModel).count()
        if total_queries == 0:
            return {
                "total_queries": 0,
                "average_response_time": 0.0,
                "average_retrieval_time": 0.0,
                "average_confidence": "N/A"
            }
            
        avg_resp = db.query(func.avg(AnalyticsEventModel.response_time_seconds)).scalar()
        avg_ret = db.query(func.avg(AnalyticsEventModel.retrieval_time_seconds)).scalar()
        
        # Simple mode confidence
        confidences = [r[0] for r in db.query(AnalyticsEventModel.confidence_score).all()]
        avg_conf = max(set(confidences), key=confidences.count) if confidences else "UNKNOWN"
        
        return {
            "total_queries": total_queries,
            "average_response_time": round(avg_resp or 0, 2),
            "average_retrieval_time": round(avg_ret or 0, 3),
            "average_confidence": avg_conf
        }

    @staticmethod
    def get_knowledge_base_metrics():
        db = next(get_db())
        total_docs = db.query(DocumentModel).count()
        most_used = db.query(DocumentAnalyticsModel).order_by(DocumentAnalyticsModel.retrieval_count.desc()).first()
        
        # Unused documents are those in DocumentModel but not in DocumentAnalyticsModel (or with 0 retrievals)
        used_ids = [r[0] for r in db.query(DocumentAnalyticsModel.document_name).all()]
        unused = db.query(DocumentModel).filter(DocumentModel.filename.not_in(used_ids)).count()
        
        return {
            "total_documents": total_docs,
            "most_used_document": most_used.document_name if most_used else "None",
            "unused_documents": unused
        }

    @staticmethod
    def get_feedback_metrics():
        db = next(get_db())
        fb = db.query(FeedbackAnalyticsModel).first()
        if not fb:
            return {
                "helpful_percentage": 0,
                "total_feedback": 0
            }
            
        return {
            "helpful_percentage": round(fb.helpfulness_percentage, 1),
            "total_feedback": fb.total_helpful + fb.total_not_helpful
        }
