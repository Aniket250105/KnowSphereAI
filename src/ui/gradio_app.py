import gradio as gr
import uuid
import os
from src.ui.api_client import APIClient
from src.ui.admin_dashboard import render_admin_dashboard
from src.ui.evaluation_dashboard import render_evaluation_dashboard
from src.ui.agent_dashboard import render_agent_dashboard

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

def generate_session_id():
    return str(uuid.uuid4())

def handle_upload(file_obj):
    if not file_obj:
        return "No file selected."
    try:
        response = APIClient.upload_document(file_obj.name)
        return f"Successfully indexed {response['filename']}. Generated {response['chunk_count']} chunks."
    except Exception as e:
        return f"Upload failed: {str(e)}"

def refresh_documents():
    try:
        docs = APIClient.get_documents()
        return [[d["id"], d["filename"], d["status"], d["chunk_count"]] for d in docs]
    except:
        return []

def delete_doc(doc_id):
    if not doc_id:
        return "Provide an ID", refresh_documents()
    try:
        APIClient.delete_document(doc_id)
        return f"Deleted {doc_id}", refresh_documents()
    except Exception as e:
        return f"Delete failed: {str(e)}", refresh_documents()

def handle_chat_stream(message, history, session_id):
    if not session_id:
        session_id = generate_session_id()
    
    history.append((message, ""))
    
    current_answer = ""
    last_message_id = None
    confidence_text = ""
    suggestions_text = ""
    
    try:
        for event in APIClient.chat_stream(message, session_id):
            if event["type"] == "token" and event.get("content"):
                current_answer += event["content"]
                history[-1] = (message, current_answer)
                yield "", history, session_id, last_message_id, confidence_text, suggestions_text
            elif event["type"] == "metadata":
                metadata = event.get("metadata", {})
                last_message_id = metadata.get("message_id")
                confidence_text = f"**Confidence**: {metadata.get('confidence', 'UNKNOWN')}"
                
                sugs = metadata.get("suggestions", [])
                if sugs:
                    suggestions_text = "**Suggested Questions:**\n" + "\n".join([f"- {s}" for s in sugs])
                    
                yield "", history, session_id, last_message_id, confidence_text, suggestions_text
            elif event["type"] == "error":
                current_answer += f"\n\n**Error**: {event.get('content')}"
                history[-1] = (message, current_answer)
                yield "", history, session_id, last_message_id, confidence_text, suggestions_text
    except Exception as e:
        history[-1] = (message, current_answer + f"\n\n**Network Error**: {str(e)}")
        yield "", history, session_id, last_message_id, confidence_text, suggestions_text

def submit_positive_feedback(msg_id):
    if not msg_id:
        return "No message to rate."
    try:
        APIClient.submit_feedback(msg_id, "HELPFUL")
        return "Feedback 'HELPFUL' submitted!"
    except Exception as e:
        return str(e)

def submit_negative_feedback(msg_id):
    if not msg_id:
        return "No message to rate."
    try:
        APIClient.submit_feedback(msg_id, "NOT_HELPFUL")
        return "Feedback 'NOT_HELPFUL' submitted!"
    except Exception as e:
        return str(e)

def load_settings():
    try:
        health = APIClient.get_health()
        return health.get("llm_status", "unknown"), health.get("embedding_model_status", "unknown"), health.get("vector_db_status", "unknown"), health.get("api_status", "unknown")
    except:
        return "error", "error", "error", "error"

def get_export_url(session_id):
    if not session_id:
        return "No active session to export."
    return f"Download TXT: {API_BASE_URL}/chat/export/{session_id}?format=txt\nDownload Markdown: {API_BASE_URL}/chat/export/{session_id}?format=markdown"

with gr.Blocks(title="KnowSphere AI Production", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🧠 KnowSphere AI Enterprise")
    
    session_id_state = gr.State(generate_session_id)
    last_msg_id_state = gr.State(None)
    auth_token_state = gr.State(None)

    
    with gr.Tabs():
        
        # TAB 1: CHAT
        with gr.Tab("Chat"):
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(height=600, bubble_full_width=False)
                    msg_input = gr.Textbox(label="Type your query here...")
                    with gr.Row():
                        send_btn = gr.Button("Send", variant="primary")
                        clear_btn = gr.Button("Clear Chat")
                        
                with gr.Column(scale=1):
                    gr.Markdown("### Response Intelligence")
                    conf_display = gr.Markdown("**Confidence**: N/A")
                    sug_display = gr.Markdown("**Suggested Questions:**\nN/A")
                    
                    gr.Markdown("### Feedback")
                    with gr.Row():
                        upvote_btn = gr.Button("👍 Helpful")
                        downvote_btn = gr.Button("👎 Not Helpful")
                    feedback_status = gr.Textbox(label="Status", interactive=False)
                    
            # Wiring Chat
            chat_event = msg_input.submit(
                handle_chat_stream,
                inputs=[msg_input, chatbot, session_id_state],
                outputs=[msg_input, chatbot, session_id_state, last_msg_id_state, conf_display, sug_display]
            )
            send_btn.click(
                handle_chat_stream,
                inputs=[msg_input, chatbot, session_id_state],
                outputs=[msg_input, chatbot, session_id_state, last_msg_id_state, conf_display, sug_display]
            )
            clear_btn.click(lambda: ([], generate_session_id(), None, "**Confidence**: N/A", "**Suggested Questions:**\nN/A"), None, [chatbot, session_id_state, last_msg_id_state, conf_display, sug_display])
            
            # Wiring Feedback
            upvote_btn.click(submit_positive_feedback, inputs=[last_msg_id_state], outputs=[feedback_status])
            downvote_btn.click(submit_negative_feedback, inputs=[last_msg_id_state], outputs=[feedback_status])
            
        # TAB 2: DOCUMENTS
        with gr.Tab("Documents"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Upload New Document")
                    file_input = gr.File(label="Select File")
                    upload_btn = gr.Button("Upload & Index", variant="primary")
                    upload_status = gr.Textbox(label="Upload Status", interactive=False)
                
                with gr.Column():
                    gr.Markdown("### Delete Document")
                    del_input = gr.Textbox(label="Document ID")
                    del_btn = gr.Button("Delete", variant="stop")
                    del_status = gr.Textbox(label="Deletion Status", interactive=False)
                    
            gr.Markdown("### Indexed Documents")
            doc_table = gr.Dataframe(headers=["ID", "Filename", "Status", "Chunks"], interactive=False)
            refresh_btn = gr.Button("Refresh Table")
            
            # Wiring Docs
            upload_btn.click(handle_upload, inputs=[file_input], outputs=[upload_status]).then(refresh_documents, None, doc_table)
            del_btn.click(delete_doc, inputs=[del_input], outputs=[del_status, doc_table])
            refresh_btn.click(refresh_documents, None, doc_table)
            app.load(refresh_documents, None, doc_table)
            
        # TAB 3: HISTORY
        with gr.Tab("History"):
            gr.Markdown("### Session Management")
            curr_sess = gr.Textbox(label="Current Session ID", interactive=False)
            export_links = gr.Markdown("No export available.")
            export_btn = gr.Button("Generate Export Links")
            
            app.load(lambda s: s, inputs=[session_id_state], outputs=[curr_sess])
            export_btn.click(get_export_url, inputs=[session_id_state], outputs=[export_links])
            
        # TAB 4: SETTINGS
        with gr.Tab("Settings"):
            gr.Markdown("### System Health & Status")
            with gr.Row():
                llm_status = gr.Textbox(label="LLM Status", interactive=False)
                emb_status = gr.Textbox(label="Embedding Model Status", interactive=False)
                db_status = gr.Textbox(label="Vector DB Status", interactive=False)
                api_status = gr.Textbox(label="API Status", interactive=False)
                
            refresh_health_btn = gr.Button("Refresh Health")
            refresh_health_btn.click(load_settings, None, [llm_status, emb_status, db_status, api_status])
            app.load(load_settings, None, [llm_status, emb_status, db_status, api_status])

        # TAB 5: ADMIN DASHBOARD
        with gr.Tab("Admin Dashboard"):
            render_admin_dashboard()
            
        # TAB 6: EVALUATION DASHBOARD
        with gr.Tab("Evaluation Dashboard"):
            render_evaluation_dashboard()

        # TAB 7: AI AGENT DASHBOARD
        with gr.Tab("AI Agent"):
            render_agent_dashboard()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
