import json
from pathlib import Path
from src.analytics.metrics_collector import MetricsCollector
from src.analytics.query_analyzer import QueryAnalyzer
import os

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

class ReportGenerator:
    @staticmethod
    def generate_reports():
        sys_metrics = MetricsCollector.get_system_metrics()
        kb_metrics = MetricsCollector.get_knowledge_base_metrics()
        fb_metrics = MetricsCollector.get_feedback_metrics()
        
        pop_queries = QueryAnalyzer.get_popular_queries(3)
        fail_queries = QueryAnalyzer.get_failed_queries(3)
        
        # JSON Report
        report_data = {
            "total_queries": sys_metrics["total_queries"],
            "average_response_time": sys_metrics["average_response_time"],
            "average_confidence": sys_metrics["average_confidence"],
            "total_documents": kb_metrics["total_documents"],
            "most_used_document": kb_metrics["most_used_document"],
            "feedback_helpful_percentage": fb_metrics["helpful_percentage"]
        }
        
        with open(REPORTS_DIR / "weekly_report.json", "w") as f:
            json.dump(report_data, f, indent=4)
            
        # Markdown Report
        md_content = f"""# KnowSphere AI Weekly Report

## Usage
Queries: {sys_metrics["total_queries"]}
Average Response Time: {sys_metrics["average_response_time"]} seconds
Average Confidence: {sys_metrics["average_confidence"]}

## Documents
Total Documents: {kb_metrics["total_documents"]}
Most Used Document: {kb_metrics["most_used_document"]}

## Feedback
Positive: {fb_metrics["helpful_percentage"]}%

## Top Queries
"""
        for q in pop_queries:
            md_content += f"- {q['query']} ({q['count']} times)\n"
            
        md_content += "\n## Failed Queries\n"
        for q in fail_queries:
            md_content += f"- {q['query']} (Reason: {q['reason']})\n"
            
        with open(REPORTS_DIR / "monthly_report.md", "w") as f:
            f.write(md_content)
            
        return {"status": "success", "message": "Reports generated in reports/"}
