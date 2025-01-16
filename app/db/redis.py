from redis.asyncio import Redis, ConnectionPool
from functools import lru_cache
from app.core.config import get_settings

settings = get_settings()

@lru_cache()
def get_redis_pool() -> ConnectionPool:
    """Get a Redis connection pool"""
    return ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        encoding='utf-8'
    )

@lru_cache()
def get_redis() -> Redis:
    """Get a Redis client instance"""
    return Redis(connection_pool=get_redis_pool())

# Async context manager for redis connections
class RedisManager:
    def __init__(self):
        self.redis_client = None
        
    async def __aenter__(self) -> Redis:
        self.redis_client = get_redis()
        return self.redis_client
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            
redis = RedisManager()