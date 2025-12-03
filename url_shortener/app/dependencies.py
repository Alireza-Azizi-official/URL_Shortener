from fastapi import Request
from redis.asyncio import from_url

from app.config import settings

_redis_client = None
async def init_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = await from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def get_redis(request: Request):
    return request.app.state.redis
