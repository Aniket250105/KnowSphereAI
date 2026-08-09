from typing import Dict, Any

class AgentAnalytics:
    """
    Observer for tracking Agent metrics without modifying existing models.
    Stores metrics in-memory for Phase 9A.
    """
    _metrics = {
        "total_executions": 0,
        "tool_usage": {},
        "tool_failures": {},
        "total_latency_seconds": 0.0
    }

    @classmethod
    def record_execution(cls, duration_seconds: float):
        cls._metrics["total_executions"] += 1
        cls._metrics["total_latency_seconds"] += duration_seconds

    @classmethod
    def record_tool_usage(cls, tool_name: str, success: bool = True):
        cls._metrics["tool_usage"][tool_name] = cls._metrics["tool_usage"].get(tool_name, 0) + 1
        if not success:
            cls._metrics["tool_failures"][tool_name] = cls._metrics["tool_failures"].get(tool_name, 0) + 1

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        total = cls._metrics["total_executions"]
        avg_latency = (cls._metrics["total_latency_seconds"] / total) if total > 0 else 0.0
        return {
            "total_executions": total,
            "average_latency_seconds": avg_latency,
            "tool_usage": dict(cls._metrics["tool_usage"]),
            "tool_failures": dict(cls._metrics["tool_failures"])
        }
