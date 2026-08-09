from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import models

class DatabaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ==========================
    # Documents
    # ==========================
    async def create_document(self, document_id: str, document_hash: str, filename: str, file_type: str, path: str, chunk_count: int, status: str) -> models.DocumentModel:
        db_doc = models.DocumentModel(
            id=document_id,
            document_hash=document_hash,
            filename=filename,
            file_type=file_type,
            path=path,
            chunk_count=chunk_count,
            status=status
        )
        self.session.add(db_doc)
        await self.session.commit()
        await self.session.refresh(db_doc)
        return db_doc

    async def get_document(self, document_id: str) -> Optional[models.DocumentModel]:
        result = await self.session.execute(select(models.DocumentModel).where(models.DocumentModel.id == document_id))
        return result.scalars().first()

    async def get_all_documents(self) -> List[models.DocumentModel]:
        result = await self.session.execute(select(models.DocumentModel).where(models.DocumentModel.status != "DELETED"))
        return list(result.scalars().all())
        
    async def update_document_status(self, document_id: str, status: str):
        db_doc = await self.get_document(document_id)
        if db_doc:
            db_doc.status = status
            await self.session.commit()
            await self.session.refresh(db_doc)
        return db_doc

    # ==========================
    # Sessions & Messages
    # ==========================
    async def create_session(self, session_id: str) -> models.SessionModel:
        # Avoid creating duplicates
        result = await self.session.execute(select(models.SessionModel).where(models.SessionModel.session_id == session_id))
        existing = result.scalars().first()
        if existing:
            return existing
            
        db_session = models.SessionModel(id=session_id, session_id=session_id)
        self.session.add(db_session)
        await self.session.commit()
        await self.session.refresh(db_session)
        return db_session

    async def save_message(self, session_id: str, role: str, content: str) -> models.MessageModel:
        # Ensure session exists
        await self.create_session(session_id)
        
        db_msg = models.MessageModel(
            session_id=session_id,
            role=role,
            content=content
        )
        self.session.add(db_msg)
        
        # Update last_active
        result = await self.session.execute(select(models.SessionModel).where(models.SessionModel.session_id == session_id))
        db_session = result.scalars().first()
        if db_session:
            db_session.last_active = db_msg.timestamp
            
        await self.session.commit()
        await self.session.refresh(db_msg)
        return db_msg

    async def get_session_messages(self, session_id: str) -> List[models.MessageModel]:
        result = await self.session.execute(
            select(models.MessageModel)
            .where(models.MessageModel.session_id == session_id)
            .order_by(models.MessageModel.id.asc())
        )
        return list(result.scalars().all())

    async def get_session_history(self, session_id: str) -> List[models.MessageModel]:
        return await self.get_session_messages(session_id)

    # ==========================
    # Users
    # ==========================
    async def create_user(self, username: str, email: str, password_hash: str, organization_id: int) -> models.UserModel:
        db_user = models.UserModel(
            username=username,
            email=email,
            password_hash=password_hash,
            organization_id=organization_id,
            role="USER"
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_user(self, user_id: int = None, email: str = None, username: str = None) -> Optional[models.UserModel]:
        from sqlalchemy import or_
        query = select(models.UserModel)
        if user_id:
            query = query.where(models.UserModel.id == user_id)
        elif email or username:
            conditions = []
            if email: conditions.append(models.UserModel.email == email)
            if username: conditions.append(models.UserModel.username == username)
            query = query.where(or_(*conditions))
        
        result = await self.session.execute(query)
        return result.scalars().first()

    # ==========================
    # Analytics & Feedback
    # ==========================
    async def save_feedback(self, message_id: int, rating: str, comment: str = None) -> models.FeedbackModel:
        db_feedback = models.FeedbackModel(
            message_id=message_id,
            rating=rating,
            comment=comment
        )
        self.session.add(db_feedback)
        await self.session.commit()
        await self.session.refresh(db_feedback)
        return db_feedback

    async def get_analytics(self) -> dict:
        # A basic aggregation for the analytics endpoint
        from sqlalchemy import func
        users_count = await self.session.execute(select(func.count(models.UserModel.id)))
        docs_count = await self.session.execute(select(func.count(models.DocumentModel.id)))
        queries_count = await self.session.execute(select(func.count(models.MessageModel.id)).where(models.MessageModel.role == "user"))
        return {
            "total_users": users_count.scalar() or 0,
            "total_documents": docs_count.scalar() or 0,
            "total_queries": queries_count.scalar() or 0
        }

    async def delete_document(self, document_id: str):
        db_doc = await self.get_document(document_id)
        if db_doc:
            await self.session.delete(db_doc)
            await self.session.commit()
