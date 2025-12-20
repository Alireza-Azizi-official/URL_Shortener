from redis.asyncio import Redis

from .config import settings
from .log_config import logger

_redis_client: Redis | None = None


async def init_redis():
    global _redis_client
    if _redis_client is None:
        logger.info("connecting to redis....")
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis_client.ping()
        logger.info("redis connection established")
    return _redis_client
