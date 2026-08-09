import gradio as gr
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/admin")

def fetch_system_metrics():
    try:
        r = requests.get(f"{API_BASE_URL}/analytics/system")
        data = r.json()
        return (
            str(data.get("total_queries", 0)),
            f"{data.get('average_response_time', 0)}s",
            str(data.get("average_confidence", "N/A"))
        )
    except:
        return "Error", "Error", "Error"

def fetch_doc_metrics():
    try:
        r = requests.get(f"{API_BASE_URL}/analytics/documents")
        data = r.json()
        popular = ", ".join([d["document_name"] for d in data.get("popular_documents", [])])
        unused = str(len(data.get("unused_documents", [])))
        return popular or "None", unused
    except:
        return "Error", "Error"

def fetch_user_metrics():
    try:
        r = requests.get(f"{API_BASE_URL}/analytics/users")
        return str(r.json().get("active_sessions", 0))
    except:
        return "Error"

def fetch_feedback_metrics():
    try:
        r = requests.get(f"{API_BASE_URL}/analytics/feedback")
        data = r.json()
        return f"{data.get('helpful_percentage', 0)}%", str(data.get('total_feedback', 0))
    except:
        return "Error", "Error"

def generate_reports():
    try:
        r = requests.post(f"{API_BASE_URL}/reports/generate")
        return r.json().get("message", "Generated")
    except Exception as e:
        return str(e)

def render_admin_dashboard():
    gr.Markdown("## Enterprise Analytics Dashboard")
    
    with gr.Row():
        with gr.Column(variant="panel"):
            gr.Markdown("### System Overview")
            total_q = gr.Textbox(label="Total Queries", interactive=False)
            avg_lat = gr.Textbox(label="Average Latency", interactive=False)
            avg_conf = gr.Textbox(label="Avg Confidence", interactive=False)
        with gr.Column(variant="panel"):
            gr.Markdown("### User Analytics")
            active_users = gr.Textbox(label="Active Sessions", interactive=False)
        with gr.Column(variant="panel"):
            gr.Markdown("### Feedback Analytics")
            helpful_pct = gr.Textbox(label="Helpful %", interactive=False)
            total_fb = gr.Textbox(label="Total Feedback", interactive=False)
            
    with gr.Row():
        with gr.Column(variant="panel"):
            gr.Markdown("### Document Analytics")
            pop_docs = gr.Textbox(label="Most Accessed", interactive=False)
            unused_docs = gr.Textbox(label="Unused Docs", interactive=False)
        with gr.Column(variant="panel"):
            gr.Markdown("### Reporting")
            gen_btn = gr.Button("Generate Reports (Weekly/Monthly)", variant="primary")
            report_status = gr.Textbox(label="Status", interactive=False)
            
    # Refresh buttons
    refresh_btn = gr.Button("Refresh Dashboard")
    
    # Event wiring
    refresh_btn.click(
        fetch_system_metrics, outputs=[total_q, avg_lat, avg_conf]
    ).then(
        fetch_user_metrics, outputs=[active_users]
    ).then(
        fetch_feedback_metrics, outputs=[helpful_pct, total_fb]
    ).then(
        fetch_doc_metrics, outputs=[pop_docs, unused_docs]
    )
    
    gen_btn.click(generate_reports, outputs=[report_status])
