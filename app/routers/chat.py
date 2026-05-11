from fastapi import APIRouter, HTTPException, Request
import hashlib
import json
import logging

from app.models.schemas import ChatRequest, ChatResponse
from app.services.redis_client import redis_client
from app.services.openai_client import openai_client
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

RATE_LIMIT_RPM = 60


def _cache_key(request: ChatRequest) -> str:
    payload = {
        "messages": [m.model_dump() for m in request.messages],
        "model": request.model or settings.openai_model,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
    }

    raw = json.dumps(payload, sort_keys=True)
    return f"chat:{hashlib.sha256(raw.encode()).hexdigest()}"


async def _check_rate_limit(client_ip: str):
    key = f"ratelimit:{client_ip}"
    count = await redis_client.incr(key, ttl=60)

    if count > RATE_LIMIT_RPM:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded."
        )


@router.post("/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest, req: Request):
    client_ip = req.client.host
    await _check_rate_limit(client_ip)

    cache_key = _cache_key(request)

    if request.use_cache:
        cached = await redis_client.get(cache_key)

        if cached:
            data = json.loads(cached)
            return ChatResponse(**data, cached=True)

    try:
        result = await openai_client.chat_completion(
            messages=[m.model_dump() for m in request.messages],
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=502, detail="Upstream API error.")

    response = ChatResponse(
        response=result["choices"][0]["message"]["content"],
        model=result.get("model", settings.openai_model),
        usage=result.get("usage"),
        latency_ms=result.get("_latency_ms"),
    )

    if request.use_cache:
        await redis_client.set(cache_key, response.model_dump_json())

    return response
