import redis.asyncio as redis
from core.config import REDIS_URL
from core.logger import logger


class RedisClient:

    _instance = None
    _redis = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        if self._redis is None:
            self._redis = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                max_connections=10,
                socket_connect_timeout=5
            )
            logger.info("Redis connected")
        return self._redis
    
    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis disconnected")
    
    def get_client(self) -> redis.Redis:
        if self._redis is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._redis


redis_client = RedisClient()
