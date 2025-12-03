from app.db import get_session
from app.dependencies import get_redis
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.shortener_service import (
    create_short_url,
    get_original_url,
    get_stats,
)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/api/v1', tags=['URL'])


@router.post("/shorten", response_model=ShortenResponse)
async def shorten(payload: ShortenRequest, session: AsyncSession = Depends(get_session), redis=Depends(get_redis)):
    try:
        return await create_short_url(payload.url, session, redis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{short_code}")
async def redirect_short(short_code: str, session: AsyncSession = Depends(get_session), redis=Depends(get_redis)):
    original = await get_original_url(short_code, session, redis)
    if not original:
        raise HTTPException(status_code=404, detail="short code not found")
    return RedirectResponse(url=original, status_code=307)


@router.get("/stats/{short_code}", response_model=StatsResponse)
async def stats(short_code: str, session: AsyncSession = Depends(get_session), redis=Depends(get_redis)):
    return await get_stats(short_code, session, redis)
