from fastapi import APIRouter, Depends
from src.analytics.metrics_collector import MetricsCollector
from src.analytics.query_analyzer import QueryAnalyzer
from src.documents.document_analytics import DocumentAnalyticsService
from src.analytics.report_generator import ReportGenerator
from src.auth.permissions import require_role
from src.api.dependencies import get_db_repository

admin_router = APIRouter()


@admin_router.get("/analytics/system")
def get_system_metrics(current_user = Depends(require_role("MANAGER"))):
    return MetricsCollector.get_system_metrics()


@admin_router.get("/analytics/documents")
def get_document_analytics(current_user = Depends(require_role("MANAGER"))):

    return {
        "health": DocumentAnalyticsService.get_document_health(),
        "popular_documents": DocumentAnalyticsService.get_popular_documents(),
        "unused_documents": DocumentAnalyticsService.get_unused_documents()
    }

@admin_router.get("/analytics/users")
async def get_user_analytics(
    current_user = Depends(require_role("ADMIN")),
    db_repo = Depends(get_db_repository)
):
    analytics = await db_repo.get_analytics()
    return analytics

@admin_router.get("/analytics/queries")
def get_query_analytics(current_user = Depends(require_role("MANAGER"))):

    return {
        "popular_queries": QueryAnalyzer.get_popular_queries(),
        "failed_queries": QueryAnalyzer.get_failed_queries()
    }

@admin_router.get("/analytics/feedback")
def get_feedback_metrics(current_user = Depends(require_role("MANAGER"))):

    return MetricsCollector.get_feedback_metrics()

@admin_router.post("/reports/generate")
def generate_reports(current_user = Depends(require_role("MANAGER"))):

    return ReportGenerator.generate_reports()
