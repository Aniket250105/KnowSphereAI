import httpx
from typing import Dict, Any, Iterator
import os
import json

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

class APIClient:
    """Client for communicating with the FastAPI backend."""
    
    token = None

    @classmethod
    def _get_headers(cls) -> Dict[str, str]:
        if cls.token:
            return {"Authorization": f"Bearer {cls.token}"}
        return {}
    
    @classmethod
    def upload_document(cls, file_path: str) -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = httpx.post(f"{API_BASE_URL}/upload", files=files, headers=cls._get_headers(), timeout=60.0)
        response.raise_for_status()

        return response.json()
        
    @classmethod
    def chat(cls, message: str, session_id: str) -> Dict[str, Any]:
        payload = {
            "message": message,
            "session_id": session_id
        }
        response = httpx.post(f"{API_BASE_URL}/chat", json=payload, headers=cls._get_headers(), timeout=120.0)

        response.raise_for_status()
        return response.json()

    @classmethod
    def chat_stream(cls, message: str, session_id: str) -> Iterator[Dict[str, Any]]:
        payload = {
            "message": message,
            "session_id": session_id
        }
        # Use httpx streaming
        with httpx.Client(timeout=120.0, headers=cls._get_headers()) as client:
            with client.stream("POST", f"{API_BASE_URL}/chat/stream", json=payload) as response:

                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            pass
                            
    @classmethod
    def submit_feedback(cls, message_id: int, rating: str, comment: str = None) -> Dict[str, Any]:
        payload = {
            "message_id": message_id,
            "rating": rating,
            "comment": comment
        }
        response = httpx.post(f"{API_BASE_URL}/feedback", json=payload, headers=cls._get_headers(), timeout=10.0)

        response.raise_for_status()
        return response.json()
        
    @classmethod
    def get_health(cls) -> Dict[str, Any]:
        response = httpx.get(f"{API_BASE_URL}/health", headers=cls._get_headers(), timeout=10.0)

        response.raise_for_status()
        return response.json()
        
    @classmethod
    def get_documents(cls) -> list:
        response = httpx.get(f"{API_BASE_URL}/documents", headers=cls._get_headers(), timeout=10.0)

        response.raise_for_status()
        return response.json()
        
    @classmethod
    def delete_document(cls, document_id: str) -> Dict[str, Any]:
        response = httpx.delete(f"{API_BASE_URL}/documents/{document_id}", headers=cls._get_headers(), timeout=10.0)

        response.raise_for_status()
        return response.json()
