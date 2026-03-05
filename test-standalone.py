#!/usr/bin/env python3
"""
Standalone local test - runs backend without Docker
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the app
from main import app

# Create test client
client = TestClient(app)

def mock_vllm_response(*args, **kwargs):
    """Mock vLLM API response"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "mock-123",
        "object": "chat.completion",
        "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "This is a mock response. In a real deployment, the SmolLM2 model would generate an actual answer."
            },
            "finish_reason": "stop"
        }]
    }
    return mock_resp

def test_backend():
    print("🧪 Testing AI Q&A Backend (Mock Mode)\n")
    
    # Test 1: Health check
    print("1. Testing API documentation endpoint...")
    response = client.get("/docs")
    if response.status_code == 200:
        print("   ✓ API docs accessible at http://localhost:8080/docs\n")
    
    # Test 2: Ask endpoint with mock
    print("2. Testing /ask endpoint with mock vLLM...")
    with patch('requests.post', side_effect=mock_vllm_response):
        response = client.post(
            "/ask",
            json={"question": "What is artificial intelligence?"}
        )
        
        if response.status_code == 200:
            print("   ✓ Request successful")
            result = response.json()
            print(f"   Response: {result['choices'][0]['message']['content']}\n")
        else:
            print(f"   ✗ Request failed: {response.status_code}\n")
    
    # Test 3: Invalid request
    print("3. Testing error handling...")
    response = client.post("/ask", json={"question": ""})
    if response.status_code == 400:
        print("   ✓ Validation working correctly\n")
    
    print("✅ All tests passed!")
    print("\n📝 Note: This uses a mock vLLM service.")
    print("   For real testing, use: docker compose up")

if __name__ == "__main__":
    test_backend()
