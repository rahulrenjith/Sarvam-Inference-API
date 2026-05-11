import redis.asyncio as aioredis
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None
        self._available = False

    async def connect(self):
        try:
            self._client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._client.ping()
            self._available = True
            logger.info("Redis connected.")
        except Exception as e:
            self._available = False
            logger.warning(f"Redis unavailable: {e}")

    async def disconnect(self):
        if self._client:
            await self._client.aclose()

    async def get(self, key: str):
        if not self._available or not self._client:
            return None
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: int = None):
        if not self._available or not self._client:
            return
        await self._client.setex(
            key,
            ttl or settings.redis_ttl_seconds,
            value
        )

    async def incr(self, key: str, ttl: int = 60):
        if not self._available or not self._client:
            return 0

        pipe = self._client.pipeline()
        await pipe.incr(key)
        await pipe.expire(key, ttl)
        result = await pipe.execute()
        return result[0]

    @property
    def is_available(self):
        return self._available


redis_client = RedisClient()
