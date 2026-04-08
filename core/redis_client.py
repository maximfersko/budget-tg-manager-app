import redis.asyncio as redis

from core.config import REDIS_URL


class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)

    async def close(self):
        if self.redis:
            await self.redis.aclose()

    async def set(self, key, value, expire=None):
        await self.redis.set(key, value, ex=expire)

    async def get(self, key):
        return await self.redis.get(key)

    async def delete(self, key):
        await self.redis.delete(key)

    async def exists(self, key):
        return await self.redis.exists(key)

redis_client = RedisClient()
