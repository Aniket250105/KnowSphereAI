import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.main import app
from src.core import config

client = TestClient(app)

def test_api():
    print("=================================")
    print("KNOWSPHERE API TEST (PHASE 5)")
    print("=================================")
    
    # 1. Test Health
    print("\n1. Testing GET /health ...")
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    print(f"Health Response: {response.json()}")
    
    # 2. Test Upload
    print("\n2. Testing POST /upload ...")
    sample_file = config.DATA_DIR / "raw" / "sample.txt"
    if not sample_file.exists():
        # Create a dummy file if not exists
        sample_file.parent.mkdir(parents=True, exist_ok=True)
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("Machine learning is a field of artificial intelligence.")
            
    with open(sample_file, "rb") as f:
        response = client.post(
            "/api/v1/upload",
            files={"file": (sample_file.name, f, "text/plain")}
        )
    assert response.status_code == 200
    print(f"Upload Response: {response.json()}")
    
    # 3. Test Chat
    print("\n3. Testing POST /chat ...")
    chat_payload = {
        "message": "What is machine learning?",
        "session_id": "test_session_001"
    }
    # For CI/CD environments with no disk space, this might trigger the mocked LLM,
    # which perfectly tests the architectural piping.
    response = client.post("/api/v1/chat", json=chat_payload)
    assert response.status_code == 200
    chat_data = response.json()
    print(f"Generated Answer: {chat_data['answer'][:100]}...")
    print(f"Retrieved Sources: {len(chat_data['sources'])}")
    print("=================================\n")
    print("ALL TESTS PASSED.")

if __name__ == "__main__":
    test_api()
