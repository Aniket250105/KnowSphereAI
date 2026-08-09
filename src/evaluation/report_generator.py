import os
import json
import csv
import matplotlib
matplotlib.use('Agg') # Headless mode
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Any, List

class ReportGenerator:
    @staticmethod
    def generate(run_id: str, summary: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        """
        Generates a comprehensive benchmark report inside the reports/ directory.
        Returns the path to the report directory.
        """
        # Ensure reports dir exists
        base_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(base_dir, exist_ok=True)
        
        report_dir = os.path.join(base_dir, run_id)
        os.makedirs(report_dir, exist_ok=True)
        
        charts_dir = os.path.join(report_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        # 1. Save JSON
        json_path = os.path.join(report_dir, "report.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"summary": summary, "results": results}, f, indent=4)
            
        # 2. Save CSV
        csv_path = os.path.join(report_dir, "report.csv")
        if results:
            keys = results[0].keys()
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
                
        # 3. Save Markdown
        md_path = os.path.join(report_dir, "report.md")
        ReportGenerator._write_markdown(md_path, run_id, summary)
        
        # 4. Generate Charts
        ReportGenerator._generate_charts(charts_dir, results)
        
        return report_dir
        
    @staticmethod
    def _write_markdown(filepath: str, run_id: str, summary: Dict[str, Any]):
        md = f"# Benchmark Report: {run_id}\n\n"
        md += f"**Dataset**: {summary.get('dataset_name', 'Unknown')} (v{summary.get('dataset_version', '1.0')})\n"
        md += f"**Total Queries**: {summary.get('total_queries', 0)}\n\n"
        
        md += "## Configuration\n"
        cfg = summary.get('configuration', {})
        for k, v in cfg.items():
            md += f"- **{k}**: {v}\n"
            
        md += "\n## Metrics\n"
        md += f"- **Average Score**: {summary.get('average_score', 0):.2%}\n"
        md += f"- **Recall@5**: {summary.get('average_recall', 0):.2%}\n"
        md += f"- **MRR**: {summary.get('average_mrr', 0):.4f}\n"
        md += f"- **Grounding Score**: {summary.get('average_grounding', 0):.2%}\n"
        md += f"- **Citation Accuracy**: {summary.get('average_citation', 0):.2%}\n"
        md += f"- **Hallucination Rate**: {summary.get('hallucination_rate', 0):.2%}\n"
        md += f"- **Average Latency**: {summary.get('average_latency', 0):.2f}s\n"
        
        if 'baseline_comparison' in summary:
            md += "\n## Baseline Comparison\n"
            bc = summary['baseline_comparison']
            for metric, diff in bc.items():
                sign = "+" if diff > 0 else ""
                md += f"- **{metric}**: {sign}{diff:.2f}\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)

    @staticmethod
    def _generate_charts(charts_dir: str, results: List[Dict[str, Any]]):
        if not results:
            return
            
        latencies = [r.get('latency', 0) for r in results]
        grounding = [r.get('grounding_score', 0) for r in results]
        
        # Latency Histogram
        plt.figure(figsize=(8, 4))
        plt.hist(latencies, bins=10, color='skyblue', edgecolor='black')
        plt.title('Latency Distribution')
        plt.xlabel('Latency (seconds)')
        plt.ylabel('Frequency')
        plt.savefig(os.path.join(charts_dir, 'latency.png'))
        plt.close()
        
        # Grounding Histogram
        plt.figure(figsize=(8, 4))
        plt.hist(grounding, bins=10, color='lightgreen', edgecolor='black')
        plt.title('Grounding Score Distribution')
        plt.xlabel('Grounding Score')
        plt.ylabel('Frequency')
        plt.savefig(os.path.join(charts_dir, 'grounding.png'))
        plt.close()
