from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_tables_if_not_exist
from app.middleware import VisitLoggingMiddleware
from app.shortener import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables_if_not_exist()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.add_middleware(VisitLoggingMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok"}
