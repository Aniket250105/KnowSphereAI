from sqlalchemy.orm import Session
from src.database.models import AnalyticsEventModel, DocumentAnalyticsModel, UserAnalyticsModel, FeedbackAnalyticsModel
from src.database.database import get_db
from datetime import datetime, timezone
import json

class AnalyticsService:
    @staticmethod
    def record_query(
        session_id: str,
        query: str,
        latency_metrics: dict,
        confidence_score: str,
        citations: list
    ):
        import asyncio
        from src.database.database import AsyncSessionLocal
        from sqlalchemy import select

        async def _do_record():
            async with AsyncSessionLocal() as db:
                # 1. Store AnalyticsEvent
                event = AnalyticsEventModel(
                    session_id=session_id,
                    query=query,
                    response_time_seconds=latency_metrics.get("total_time_seconds", 0.0),
                    retrieval_time_seconds=latency_metrics.get("total_time_seconds", 0.0) - latency_metrics.get("generation_time_seconds", 0.0),
                    generation_time_seconds=latency_metrics.get("generation_time_seconds", 0.0),
                    confidence_score=confidence_score,
                    search_mode="hybrid"
                )
                db.add(event)
                
                # 2. Update UserAnalytics
                result = await db.execute(select(UserAnalyticsModel).filter(UserAnalyticsModel.session_id == session_id))
                user = result.scalars().first()
                if not user:
                    user = UserAnalyticsModel(session_id=session_id, total_queries=1, total_messages=2)
                    db.add(user)
                else:
                    user.total_queries += 1
                    user.total_messages += 2
                    user.last_activity = datetime.now(timezone.utc)
                    if getattr(user, 'first_activity', None):
                        first_act = user.first_activity
                        if first_act.tzinfo is None:
                            first_act = first_act.replace(tzinfo=timezone.utc)
                        duration = (user.last_activity - first_act).total_seconds()
                        user.average_session_duration = duration
                
                # 3. Update DocumentAnalytics
                if citations:
                    for source in citations:
                        doc_name = source.get("document")
                        score = source.get("score", 0.0)
                        
                        doc_res = await db.execute(select(DocumentAnalyticsModel).filter(DocumentAnalyticsModel.document_name == doc_name))
                        doc = doc_res.scalars().first()
                        
                        if not doc:
                            doc = DocumentAnalyticsModel(
                                document_id=doc_name,
                                document_name=doc_name,
                                retrieval_count=1,
                                average_similarity_score=score,
                                last_accessed=datetime.now(timezone.utc)
                            )
                            db.add(doc)
                        else:
                            total_score = doc.average_similarity_score * doc.retrieval_count
                            doc.retrieval_count += 1
                            doc.average_similarity_score = (total_score + score) / doc.retrieval_count
                            doc.last_accessed = datetime.now(timezone.utc)
                            
                await db.commit()
                
        asyncio.run(_do_record())

    @staticmethod
    def update_feedback(rating: str):
        import asyncio
        from src.database.database import AsyncSessionLocal
        from sqlalchemy import select

        async def _do_update():
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(FeedbackAnalyticsModel))
                fb = result.scalars().first()
                if not fb:
                    fb = FeedbackAnalyticsModel(
                        total_helpful=1 if rating == "HELPFUL" else 0,
                        total_not_helpful=1 if rating == "NOT_HELPFUL" else 0
                    )
                    db.add(fb)
                else:
                    if rating == "HELPFUL":
                        fb.total_helpful += 1
                    elif rating == "NOT_HELPFUL":
                        fb.total_not_helpful += 1
                        
                total = fb.total_helpful + fb.total_not_helpful
                fb.helpfulness_percentage = (fb.total_helpful / total) * 100 if total > 0 else 0.0
                await db.commit()
                
        asyncio.run(_do_update())
