import requests
import json
import uuid
import time

API_BASE_URL = "http://localhost:8000/api/v1"
ADMIN_BASE_URL = "http://localhost:8000/admin"

def run_tests():
    print("Testing Phase 6C Endpoints...")
    session_id = str(uuid.uuid4())
    
    print(f"\n1. Simulating Chat Request for Session: {session_id}")
    try:
        response = requests.post(f"{API_BASE_URL}/chat", json={"message": "What is AI?", "session_id": session_id})
        data = response.json()
        print(f"Chat Response received. Total Time: {data.get('total_time_seconds')}")
        time.sleep(1) # Give DB time if async (though it's sync here)
        
        print("\n2. Testing Admin Analytics Endpoints")
        
        sys_res = requests.get(f"{ADMIN_BASE_URL}/analytics/system")
        print(f"System Analytics: {sys_res.json()}")
        
        doc_res = requests.get(f"{ADMIN_BASE_URL}/analytics/documents")
        print(f"Document Analytics: {doc_res.json()}")
        
        user_res = requests.get(f"{ADMIN_BASE_URL}/analytics/users")
        print(f"User Analytics: {user_res.json()}")
        
        query_res = requests.get(f"{ADMIN_BASE_URL}/analytics/queries")
        print(f"Query Analytics Popular: {query_res.json().get('popular_queries')}")
        
        fb_res = requests.get(f"{ADMIN_BASE_URL}/analytics/feedback")
        print(f"Feedback Analytics: {fb_res.json()}")
        
        print("\n3. Testing Automated Report Generation")
        report_res = requests.post(f"{ADMIN_BASE_URL}/reports/generate")
        print(f"Report Generation: {report_res.json()}")
        
    except requests.exceptions.ConnectionError:
        print("API server is not running. Please start it to run full integration tests.")
        
if __name__ == "__main__":
    run_tests()
