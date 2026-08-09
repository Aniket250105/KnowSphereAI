from typing import List, Dict, Any

class RetrievalStrategyTester:
    def __init__(self, runner):
        self.runner = runner
        
    async def run_leaderboard(self, dataset) -> List[Dict[str, Any]]:
        """
        Runs the benchmark across Dense, Hybrid, Expanded, and Hybrid+Expanded.
        Returns a ranked list (Leaderboard).
        """
        strategies = ["Dense", "Hybrid", "Expanded", "Hybrid+Expansion"]
        results = []
        
        for strategy in strategies:
            # Inject strategy config into runner
            config = {"retrieval_mode": strategy}
            res = await self.runner.run_benchmark(dataset, profile="Quick", config=config)
            
            results.append({
                "Strategy": strategy,
                "Recall@5": res.get("average_recall", 0),
                "MRR": res.get("average_mrr", 0),
                "Latency": res.get("average_latency", 0),
                "Score": res.get("average_score", 0)
            })
            
        # Rank by Score descending
        results.sort(key=lambda x: x["Score"], reverse=True)
        return results
