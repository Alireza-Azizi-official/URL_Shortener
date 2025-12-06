from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from .db import create_tables_if_not_exist
from .kafka_consumer import close_kafka_consumer, init_kafka_consumer
from .kafka_producer import close_kafka, init_kafka
from .log_config import logger
from .middleware import VisitLoggingMiddleware
from .rate_limiter_redis import init_rate_limit_redis
from .redis_conf import init_redis
from .router import router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting application lifespan...")
    try:
        app.state.redis = await init_redis()
        logger.info("redis initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}", exc_info=True)
        raise
    try:
        rate_limit_redis = await init_rate_limit_redis()
        await FastAPILimiter.init(rate_limit_redis)
        logger.info("fastapi limiter initialized successfully.")
    except Exception as e:
        logger.error(f"failed to initialized fastapi_limiter: {e}", exc_info=True)
        raise

    try:
        await create_tables_if_not_exist()
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
        raise

    try:
        await init_kafka(app)
    except Exception as e:
        logger.error(f"failed to start kafka: {e}", exc_info=True)
        raise

    try:
        await init_kafka_consumer(app)
        logger.info("kafka consumer started")
    except Exception as e:
        logger.error(f"failed to start kafka consumer: {e}", exc_info=True)
        raise

    yield

    try:
        await close_kafka(app)
        logger.info("kafka is closed.")
    except Exception as e:
        logger.error(f"failed to close kafka: {e}", exc_info=True)
        raise
    try:
        await close_kafka_consumer(app)
        logger.info("kafka consumer shut down.")
    except Exception as e:
        logger.error(f"failed to close kafka consumer: {e}", exc_info=True)
        raise


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.add_middleware(VisitLoggingMiddleware)
