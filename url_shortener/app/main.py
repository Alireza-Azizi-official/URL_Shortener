from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi_limiter import FastAPILimiter

from .db import create_tables_if_not_exist
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
        logger.error(f"failed to initialize fastapi_limiter: {e}", exc_info=True)
        raise

    try:
        await create_tables_if_not_exist()
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
        raise

    yield


app = FastAPI(lifespan=lifespan)

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
static_dir = os.path.join(project_root, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def read_root():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "URL Shortener API"}

app.include_router(router)
app.add_middleware(VisitLoggingMiddleware)
