import requests
import json
import uuid

API_BASE_URL = "http://localhost:8000/api/v1"

def run_tests():
    print("Testing Phase 6B Endpoints...")
    session_id = str(uuid.uuid4())
    
    print(f"\n1. Testing Streaming Chat (/chat/stream) with Session: {session_id}")
    try:
        response = requests.post(f"{API_BASE_URL}/chat/stream", json={"message": "What is AI?", "session_id": session_id}, stream=True)
        message_id = None
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    data = json.loads(decoded[6:])
                    print(f"Event: {data['type']}")
                    if data['type'] == 'metadata':
                        message_id = data['metadata'].get('message_id')
                        print(f"Metadata captured. Message ID: {message_id}")
        
        if message_id:
            print(f"\n2. Testing Feedback System (/feedback) for Message ID: {message_id}")
            fb_res = requests.post(f"{API_BASE_URL}/feedback", json={
                "message_id": message_id,
                "rating": "HELPFUL",
                "comment": "Great answer via streaming!"
            })
            print(f"Feedback Status: {fb_res.json()}")
            
        print(f"\n3. Testing Export Chat (/chat/export/{session_id})")
        exp_res = requests.get(f"{API_BASE_URL}/chat/export/{session_id}?format=txt")
        print("Export snippet:")
        print(exp_res.text[:100] + "...")
        
    except requests.exceptions.ConnectionError:
        print("API server is not running. Please start it to run full integration tests.")
        
if __name__ == "__main__":
    run_tests()
