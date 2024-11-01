import requests
from typing import Dict, Optional, List
import os
from datetime import datetime

class APIClient:
    def __init__(self):
        self.base_url = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")
        self.token: Optional[str] = None

    def _get_headers(self) -> Dict:
        """Get request headers with authentication token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, email: str, password: str) -> Dict:
        """Authenticate user and get access token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/token",
                data={"username": email, "password": password}
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            return data
        except requests.RequestException as e:
            raise Exception(f"Login failed: {str(e)}")

    def fetch_documents(self, prompt_count: int = 5) -> Dict:
        """Fetch documents from backend"""
        try:
            response = requests.get(
                f"{self.base_url}/documents",
                params={"prompt_count": prompt_count},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error fetching documents: {str(e)}")

    def get_document_summary(self, document_id: str) -> Dict:
        """Generate or retrieve document summary"""
        try:
            response = requests.get(
                f"{self.base_url}/documents/{document_id}/summary",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error getting document summary: {str(e)}")

    def ask_question(self, document_id: str, question: str) -> Dict:
        """Submit question to Q/A system"""
        try:
            response = requests.post(
                f"{self.base_url}/qa/ask",
                json={"document_id": document_id, "question": question},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error processing question: {str(e)}")

    def search_documents(self, query: str, search_type: str = "all") -> Dict:
        """Search documents and research notes"""
        try:
            response = requests.get(
                f"{self.base_url}/search",
                params={"query": query, "search_type": search_type},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error searching documents: {str(e)}")

    def generate_report(self, document_id: str, options: Dict) -> Dict:
        """Generate document report"""
        try:
            response = requests.post(
                f"{self.base_url}/documents/{document_id}/report",
                json=options,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error generating report: {str(e)}")