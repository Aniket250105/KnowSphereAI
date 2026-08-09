from src.evaluation.metrics import RAGMetrics
from src.core.logger import get_logger

logger = get_logger(__name__)

class Evaluator:
    """
    Logs RAG performance metrics. Future implementations can push to a time-series DB or dashboard.
    """
    @staticmethod
    def log_metrics(metrics: RAGMetrics):
        logger.info(
            f"[METRICS] Total: {metrics.total_time_seconds:.2f}s | "
            f"Retrieval: {metrics.retrieval_time_seconds:.2f}s | "
            f"Generation: {metrics.generation_time_seconds:.2f}s | "
            f"Query: '{metrics.query}'"
        )
