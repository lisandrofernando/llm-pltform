from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/v1/chat/completions")
def chat_completions(request: dict):
    return {
        "id": "mock-response-123",
        "object": "chat.completion",
        "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": f"Mock AI Response: I received your question and here's my answer. (This is a test response since the real vLLM model isn't running)"
            },
            "finish_reason": "stop"
        }]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
