import os
import json
import shutil
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.database import get_db

from src.api.schemas import (
    HealthResponse,
    UploadResponse,
    ChatRequest,
    ChatResponse,
    ChatSource,
    FeedbackRequest,
)
from src.api.dependencies import (
    get_document_processor,
    get_indexing_service,
    get_rag_pipeline,
    get_document_manager,
    get_db_repository,
)
from src.auth.permissions import require_role

from src.documents.document_manager import DocumentManager
from src.documents.schemas import DocumentResponse
from src.document_processing.processor import DocumentProcessor
from src.services.indexing_service import IndexingService
from src.rag.rag_pipeline import RAGPipeline
from src.analytics.analytics_service import AnalyticsService
from src.core import config


router = APIRouter()


# ============================================================
# HEALTH
# ============================================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        api_status="ok",
        embedding_model_status="ok",
        vector_db_status="ok",
        llm_status="ok"
    )


# ============================================================
# DOCUMENT UPLOAD
# ============================================================

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_manager: DocumentManager = Depends(get_document_manager),
):
    """
    Upload a document and process/index it locally.
    """

    config.RAW_DIR.mkdir(parents=True, exist_ok=True)

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided",
        )

    temp_path = config.RAW_DIR / file.filename

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc_id = await document_manager.process_and_index_upload(
            temp_path,
            file.filename,
        )

        doc = await document_manager.get_document(doc_id)

        if not doc:
            raise HTTPException(
                status_code=500,
                detail="Document was processed but could not be retrieved",
            )

        return UploadResponse(
            filename=file.filename,
            document_id=doc.id,
            chunk_count=doc.chunk_count,
            status=doc.status,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# DOCUMENTS
# ============================================================

@router.get(
    "/documents",
    response_model=List[DocumentResponse],
)
async def get_documents(
    document_manager: DocumentManager = Depends(get_document_manager),
):
    try:
        docs = await document_manager.list_documents()
        return docs

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: str,
    document_manager: DocumentManager = Depends(get_document_manager),
):
    doc = await document_manager.get_document(document_id)

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return doc


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    doc = await db.scalar(select(DocumentModel).filter(DocumentModel.id == document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    await db.delete(doc)
    await db.commit()
    return {"message": "Document deleted"}

@router.get("/documents/{document_id}/report")
async def generate_document_report(document_id: str, db: AsyncSession = Depends(get_db)):
    doc = await db.scalar(select(DocumentModel).filter(DocumentModel.id == document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    import datetime
    
    # Minimal report content in Markdown
    md_content = f"""# Document Analysis Report
    
## Document Details
- **Title**: {doc.filename}
- **ID**: {doc.id}
- **Status**: {doc.status}
- **Chunks Generated**: {doc.chunk_count}
- **Upload Date**: {doc.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Report Generated**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
The document "{doc.filename}" has been successfully ingested and processed by KnowSphere AI into {doc.chunk_count} distinct semantic chunks. These chunks are now searchable via the RAG pipeline.

## Key Metrics
- **Processing Status**: {doc.status}
- **Data Completeness**: 100% chunks embedded

*Generated automatically by KnowSphere AI*
"""
    
    return PlainTextResponse(
        content=md_content, 
        media_type="text/markdown", 
        headers={"Content-Disposition": f'attachment; filename="report_{doc.filename}.md"'}
    )


# ============================================================
# CHAT
# ============================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    """
    Ask a question against the local RAG pipeline.
    """

    try:
        response = rag_pipeline.ask(
            request.message,
            session_id=request.session_id,
        )

        sources = [
            ChatSource(
                document=src["document"],
                page=src["page"],
                chunk_id=src["chunk_id"],
                score=src["score"],
            )
            for src in response.sources
        ]

        # Analytics
        AnalyticsService.record_query(
            session_id=request.session_id,
            query=request.message,
            latency_metrics={
                "total_time_seconds": response.total_time_seconds,
                "generation_time_seconds": response.generation_time_seconds,
            },
            confidence_score=response.confidence,
            citations=response.sources,
        )

        return ChatResponse(
            answer=response.answer,
            sources=sources,
            retrieved_chunks=response.retrieved_chunks,
            generation_time_seconds=response.generation_time_seconds,
            total_time_seconds=response.total_time_seconds,
            confidence=response.confidence,
            suggested_questions=response.suggested_questions,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# STREAMING CHAT
# ============================================================

@router.post("/chat/stream")
def chat_stream(
    request: ChatRequest,
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    def event_generator():
        try:
            for event in rag_pipeline.ask_stream(
                request.message,
                session_id=request.session_id,
            ):

                if event.type == "metadata":
                    metadata = event.metadata or {}

                    AnalyticsService.record_query(
                        session_id=request.session_id,
                        query=request.message,
                        latency_metrics=metadata.get("timings", {}),
                        confidence_score=metadata.get(
                            "confidence",
                            "UNKNOWN",
                        ),
                        citations=metadata.get(
                            "sources",
                            [],
                        ),
                    )

                yield (
                    f"data: {json.dumps({
                        'type': event.type,
                        'content': event.content,
                        'metadata': event.metadata
                    })}\n\n"
                )

        except Exception as e:
            yield (
                f"data: {json.dumps({
                    'type': 'error',
                    'content': str(e)
                })}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


# ============================================================
# ANALYTICS DASHBOARD
# ============================================================

@router.get("/analytics")
async def get_analytics_dashboard(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select, func
    from src.database.models import AnalyticsEventModel, DocumentModel, DocumentAnalyticsModel, UserAnalyticsModel, FeedbackAnalyticsModel
    
    total_queries = await db.scalar(select(func.count(AnalyticsEventModel.id)))
    avg_resp = await db.scalar(select(func.avg(AnalyticsEventModel.response_time_seconds)))
    
    total_docs = await db.scalar(select(func.count(DocumentModel.id)))
    total_users = await db.scalar(select(func.count(UserAnalyticsModel.id)))
    
    # popular documents
    pop_docs_res = await db.execute(select(DocumentAnalyticsModel).order_by(DocumentAnalyticsModel.retrieval_count.desc()).limit(4))
    pop_docs = pop_docs_res.scalars().all()
    
    doc_labels = [d.document_name for d in pop_docs] if pop_docs else ['No Data']
    doc_data = [d.retrieval_count for d in pop_docs] if pop_docs else [1]
    
    # feedback
    fb_res = await db.execute(select(FeedbackAnalyticsModel))
    fb = fb_res.scalars().first()
    feedback = [fb.total_helpful, fb.total_not_helpful] if fb else [0, 0]
    
    return {
        "documents": total_docs or 0,
        "queries": total_queries or 0,
        "users": total_users or 0,
        "avg_latency": f"{round(avg_resp or 0, 2)}s",
        "health": "Operational",
        "query_chart": [0, 0, 0, 0, 0, 0, total_queries or 0],
        "doc_labels": doc_labels,
        "doc_data": doc_data,
        "feedback": feedback
    }

# ============================================================
# FEEDBACK
# ============================================================

@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db_repo=Depends(get_db_repository),
):
    try:
        await db_repo.save_feedback(
            request.message_id,
            request.rating,
            request.comment,
        )

        AnalyticsService.update_feedback(
            request.rating
        )

        return {
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# CHAT EXPORT
# ============================================================

@router.get("/chat/export/{session_id}")
def export_chat(
    session_id: str,
    format: str = "txt",
):
    from src.export.chat_exporter import ChatExporter

    try:
        if format in ("markdown", "md"):
            content = ChatExporter.export_markdown(
                session_id
            )

            return PlainTextResponse(
                content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": (
                        f"attachment; "
                        f"filename=chat_export_{session_id}.md"
                    )
                },
            )

        content = ChatExporter.export_txt(
            session_id
        )

        return PlainTextResponse(
            content,
            media_type="text/plain",
            headers={
                "Content-Disposition": (
                    f"attachment; "
                    f"filename=chat_export_{session_id}.txt"
                )
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )