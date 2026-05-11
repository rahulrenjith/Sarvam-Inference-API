import httpx
import logging
import time

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self):
        self._base_url = settings.openai_base_url
        self._headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def chat_completion(
        self,
        messages,
        model=None,
        temperature=0.2,
        max_tokens=512,
    ):
        payload = {
            "model": model or settings.openai_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        start = time.perf_counter()

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers,
                json=payload,
            )

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(f"LLM latency: {latency_ms}ms")

        response.raise_for_status()

        result = response.json()
        result["_latency_ms"] = latency_ms

        return result


openai_client = OpenAIClient()
