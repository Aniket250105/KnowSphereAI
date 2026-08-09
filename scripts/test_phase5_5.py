import sys
import os
import time
from pathlib import Path
from fastapi.testclient import TestClient
from src.core import config
from src.database.database import SessionLocal
from src.database.models import DocumentModel, SessionModel, MessageModel

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.main import app

client = TestClient(app)

def test_phase5_5():
    print("=================================")
    print("KNOWSPHERE PHASE 5.5 TESTS")
    print("=================================")
    
    # 1. Upload and index document
    print("\n1. Testing Document Upload & Persistence...")
    sample_file = config.DATA_DIR / "raw" / "sample.txt"
    if not sample_file.exists():
        sample_file.parent.mkdir(parents=True, exist_ok=True)
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("A database is an organized collection of data.")
            
    with open(sample_file, "rb") as f:
        upload_res = client.post(
            "/api/v1/upload",
            files={"file": (sample_file.name, f, "text/plain")}
        )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["document_id"]
    print(f"Uploaded. Document ID: {doc_id}")
    
    # 2. Check DB Records
    print("\n2. Verifying DB Record via API...")
    docs_res = client.get("/api/v1/documents")
    assert docs_res.status_code == 200
    docs = docs_res.json()
    assert any(d["id"] == doc_id for d in docs)
    print(f"Document verified in GET /documents. Status: {docs[0]['status']}")
    
    # 3. Test Chat Session & Persistence
    print("\n3. Testing Persistent Memory...")
    session_id = "test_persist_001"
    
    # Message 1
    chat_res1 = client.post("/api/v1/chat", json={
        "message": "What is a database?",
        "session_id": session_id
    })
    
    # Message 2
    chat_res2 = client.post("/api/v1/chat", json={
        "message": "Can you explain further?",
        "session_id": session_id
    })
    
    # Verify DB directly
    db = SessionLocal()
    messages = db.query(MessageModel).filter(MessageModel.session_id == session_id).all()
    print(f"Messages found in DB for session {session_id}: {len(messages)}")
    assert len(messages) == 4 # 2 User + 2 Assistant
    
    # 4. Test Deletion
    print("\n4. Testing Document Deletion Cascade...")
    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 200
    
    # Verify it's gone
    docs_after = client.get("/api/v1/documents")
    assert not any(d["id"] == doc_id for d in docs_after.json())
    
    print("=================================\n")
    print("ALL TESTS PASSED.")

if __name__ == "__main__":
    test_phase5_5()
