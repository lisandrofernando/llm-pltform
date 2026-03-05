# Local Testing Guide

## Option 1: Quick Test with Mock (Recommended for Testing)

This uses a lightweight mock vLLM service for fast testing:

```bash
# Start services with mock
docker compose -f docker-compose.mock.yml up --build

# In another terminal, test the API
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'

# Stop services
docker compose -f docker-compose.mock.yml down
```

## Option 2: Full Test with Real vLLM (Slow, requires resources)

This downloads and runs the actual SmolLM2 model (~270MB):

```bash
# Start services with real vLLM
docker compose up --build

# Wait 3-5 minutes for model download
docker compose logs -f vllm

# Test when ready
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'

# Stop services
docker compose down
```

## Option 3: Backend Only (Manual vLLM)

Test just the backend:

```bash
cd app
source venv/bin/activate
export VLLM_URL=http://localhost:8000
uvicorn main:app --host 0.0.0.0 --port 8080
```

## API Endpoints

- **Swagger UI**: http://localhost:8080/docs
- **POST /ask**: Send questions to the LLM

### Example Request:
```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain quantum computing in simple terms"
  }'
```

### Example Response:
```json
{
  "id": "cmpl-123",
  "object": "chat.completion",
  "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Quantum computing uses quantum mechanics..."
    },
    "finish_reason": "stop"
  }]
}
```

## Troubleshooting

### Services not starting?
```bash
docker compose ps
docker compose logs
```

### Port already in use?
```bash
lsof -ti:8080 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Clean restart?
```bash
docker compose down -v
docker compose up --build
```
