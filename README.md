# Sarvam Inference API

Production-grade FastAPI service wrapping LLM APIs with:
- Redis caching
- Rate limiting
- Health diagnostics
- Async architecture
- Docker support

## Features
- FastAPI async APIs
- Redis caching layer
- Health and readiness probes
- Request logging middleware
- Retry logic for LLM APIs
- Dockerized deployment

## Run Locally

```bash
git clone <repo>
cd sarvam-inference-api
cp .env.example .env
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run:
```bash
uvicorn app.main:app --reload
```

Open:
- http://localhost:8000/docs

## Docker

```bash
docker compose up --build
```

## Sample Request

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ]
}'
```
