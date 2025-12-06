import redis.asyncio as redis

from app.config import settings
from app.log_config import logger

_rate_limit_redis = None


async def init_rate_limit_redis():
    global _rate_limit_redis
    if _rate_limit_redis is None:
        try:
            logger.info("connecting to redis....")
            _rate_limit_redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("redis connection established.")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}", exc_info=True)
            raise
    return _rate_limit_redis
