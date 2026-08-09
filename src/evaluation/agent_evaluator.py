from typing import List
from src.agents.schemas import MemoryEntry

class AgentEvaluator:
    @staticmethod
    def evaluate(memory_entries: List[MemoryEntry]) -> dict:
        total = len(memory_entries)
        if total == 0:
            return {}

        total_tools = 0
        failed_tools = 0
        latencies = []

        for entry in memory_entries:
            for tool_name, result in entry.tool_outputs.items():
                total_tools += 1
                if isinstance(result, dict) and "error" in result:
                    failed_tools += 1
            if "start" in entry.timestamps and "end" in entry.timestamps:
                latency = (entry.timestamps["end"] - entry.timestamps["start"]).total_seconds()
                latencies.append(latency)

        tool_success_rate = ((total_tools - failed_tools) / total_tools) if total_tools > 0 else 1.0
        avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

        return {
            "total_executions": total,
            "tool_success_rate": tool_success_rate,
            "tool_failure_count": failed_tools,
            "average_latency_seconds": avg_latency
        }
