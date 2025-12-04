from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_tables_if_not_exist
from app.dependencies import init_redis
from app.log_config import logger
from app.middleware import VisitLoggingMiddleware
from app.router import router


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
        await create_tables_if_not_exist()
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
        raise
    yield
    logger.info("Application shutdown completed.")


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.add_middleware(VisitLoggingMiddleware)
