import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter

from .db import create_tables_if_not_exist
from .log_config import logger
from .middleware import VisitLoggingMiddleware
from .redis_conf import init_redis
from .router import router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting application lifespan...")
    redis = await init_redis()
    app.state.reids = redis
    await FastAPILimiter.init(redis)
    logger.info("fastapi limiter initialized successfully")
    await create_tables_if_not_exist()
    logger.info("database tables ensured.")
    yield
    await redis.close()


app = FastAPI(lifespan=lifespan)

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
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
