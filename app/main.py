from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)

app = FastAPI()

VLLM_URL = os.getenv("VLLM_URL", "http://vllm-service:8000")

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Q&A Backend is running", "vllm_url": VLLM_URL}

@app.get("/health")
def health():
    return {"status": "healthy", "backend": "running"}

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QuestionRequest):

    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        payload = {
            "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
            "messages": [
                {"role": "user", "content": request.question}
            ]
        }

        response = requests.post(
            f"{VLLM_URL}/v1/chat/completions",
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"vLLM error: {e}")
        raise HTTPException(status_code=500, detail="LLM service unavailable")
