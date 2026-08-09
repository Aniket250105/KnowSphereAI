import gradio as gr
from src.ui.api_client import APIClient

def run_benchmark(profile):
    # This would call the API.
    # In a full implementation, this uses APIClient to call POST /admin/evaluation/run
    return f"Benchmark '{profile}' executed successfully (Mock). Check charts below."

def render_evaluation_dashboard():
    gr.Markdown("## 📊 Evaluation & Benchmarking Dashboard")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Run Benchmark")
            profile_drp = gr.Dropdown(choices=["Quick", "Standard", "Full"], value="Quick", label="Benchmark Profile")
            run_btn = gr.Button("Run Benchmark", variant="primary")
            run_status = gr.Textbox(label="Status", interactive=False)
            run_btn.click(run_benchmark, inputs=[profile_drp], outputs=[run_status])
            
        with gr.Column():
            gr.Markdown("### Baseline Comparison (Last Run)")
            gr.Markdown("""
            **Grounding**: 91.2% (*+2.6%*)
            **Recall@5**: 88.0% (*+1.1%*)
            **Latency**: 1.5s (*-0.2s*)
            """)
            
    with gr.Tabs():
        with gr.Tab("Charts & Trends"):
            gr.Markdown("*(Placeholder for Matplotlib Trends - usually populated dynamically from API)*")
            with gr.Row():
                # Usually we would render gr.Image or gr.Plot here with the generated pngs
                gr.Markdown("📈 **Grounding Score vs Time**")
                gr.Markdown("📈 **Average Latency vs Time**")
                
        with gr.Tab("Leaderboards"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Prompt Leaderboard")
                    gr.Dataframe(
                        headers=["Prompt Version", "Grounding", "Latency", "Winner"],
                        value=[["v1.0", "88%", "1.4s", ""], ["v2.0", "92%", "1.6s", "🏆"]],
                        interactive=False
                    )
                with gr.Column():
                    gr.Markdown("### Retrieval Strategy Leaderboard")
                    gr.Dataframe(
                        headers=["Strategy", "Recall@5", "MRR", "Latency"],
                        value=[
                            ["Hybrid+Expansion", "94%", "0.92", "1.8s"],
                            ["Hybrid", "88%", "0.85", "1.2s"],
                            ["Dense", "82%", "0.78", "0.9s"]
                        ],
                        interactive=False
                    )
                    
        with gr.Tab("Failure Explorer"):
            gr.Markdown("### Failed Queries Analysis")
            gr.Dataframe(
                headers=["Query", "Expected", "Generated", "Failure Reason"],
                value=[
                    ["What is X?", "X is Y", "X is Z", "Hallucination"],
                    ["Explain A", "A means B", "I don't know", "Low recall"]
                ],
                interactive=False
            )
