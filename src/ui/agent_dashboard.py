import gradio as gr
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

def execute_agent_query(query: str, agent_type: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/agent/chat",
            json={"query": query, "agent_type": agent_type}
        )
        if response.status_code == 200:
            data = response.json()
            return (
                f"Agent Type: {data.get('agent_type')}\n"
                f"Latency: {data.get('latency', 0):.2f}s",
                data.get("response", "")
            )
        else:
            return f"Error: {response.status_code}", response.text
    except Exception as e:
        return "Connection Error", str(e)

def render_agent_dashboard():
    gr.Markdown("## 🤖 AI Agent Dashboard (Phase 9A)")
    
    with gr.Row():
        query_input = gr.Textbox(label="Agent Request", placeholder="e.g. Calculate 52 * 12.5 and find KnowSphere revenue.")
        agent_type = gr.Dropdown(choices=["simple", "workflow", "rag"], value="workflow", label="Agent Type")
    
    submit_btn = gr.Button("Execute", variant="primary")
    
    with gr.Row():
        execution_trace = gr.Textbox(label="Execution Trace & Metadata", interactive=False, lines=5)
        final_response = gr.Textbox(label="Final Response", interactive=False, lines=5)
        
    submit_btn.click(
        fn=execute_agent_query,
        inputs=[query_input, agent_type],
        outputs=[execution_trace, final_response]
    )
