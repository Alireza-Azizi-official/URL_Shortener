from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_tables_if_not_exist
from app.dependencies import init_redis
from app.middleware import VisitLoggingMiddleware
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await init_redis()
    await create_tables_if_not_exist()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.add_middleware(VisitLoggingMiddleware)
