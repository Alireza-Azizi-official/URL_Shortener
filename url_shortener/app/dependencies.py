from fastapi import Request
from redis.asyncio import from_url

from app.config import settings
from app.log_config import logger

_redis_client = None


async def init_redis():
    global _redis_client
    if _redis_client is None:
        logger.info("connecting to redis....")
        _redis_client = await from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("redis connection established.")
    return _redis_client


async def get_redis(request: Request):
    return request.app.state.redis
