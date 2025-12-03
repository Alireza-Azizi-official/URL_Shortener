from fastapi import FastAPI

from app import shortener
from app.config import settings
from app.db import create_tables_if_not_exist
from app.middleware import VisitLoggingMiddleware

app = FastAPI()
app.include_router(shortener.router)
app.add_middleware(VisitLoggingMiddleware)


@app.on_event("startup")
async def startup():
    await create_tables_if_not_exist()


@app.get("/health")
async def health():
    return {"status": "ok"}
