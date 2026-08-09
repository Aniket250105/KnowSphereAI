from src.database.database import get_db
from src.database.models import DocumentModel, DocumentAnalyticsModel

class DocumentAnalyticsService:
    @staticmethod
    def get_popular_documents(limit: int = 5):
        db = next(get_db())
        docs = db.query(DocumentAnalyticsModel).order_by(DocumentAnalyticsModel.retrieval_count.desc()).limit(limit).all()
        return [{"document_name": d.document_name, "retrievals": d.retrieval_count} for d in docs]

    @staticmethod
    def get_unused_documents():
        db = next(get_db())
        used_names = [r[0] for r in db.query(DocumentAnalyticsModel.document_name).all()]
        unused = db.query(DocumentModel).filter(DocumentModel.filename.not_in(used_names)).all()
        return [{"filename": d.filename, "chunk_count": d.chunk_count} for d in unused]

    @staticmethod
    def get_document_health():
        db = next(get_db())
        total = db.query(DocumentModel).count()
        if total == 0:
            return {"health": "No Documents", "total": 0, "unused": 0}
        
        unused = len(DocumentAnalyticsService.get_unused_documents())
        health_score = ((total - unused) / total) * 100
        
        return {
            "health_score": round(health_score, 1),
            "total_documents": total,
            "unused_documents": unused
        }
