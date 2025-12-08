from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .redis_conf import get_redis
from .schemas import ShortenRequest, ShortenResponse, StatsResponse
from .shortener_service import (
    create_short_url,
    get_original_url,
    get_stats,
    get_visits_paginated,
)
from fastapi_limiter.depends import RateLimiter


router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse, dependencies=[Depends(RateLimiter(times=300, seconds=60))])
async def shorten(payload: ShortenRequest, request: Request, session: AsyncSession = Depends(get_session), redis=Depends(get_redis)):
    try:
        return await create_short_url(payload.url, session, redis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{short_code}", dependencies=[Depends(RateLimiter(times=300, seconds=60))])
async def redirect_short(short_code: str, request: Request, session: AsyncSession = Depends(get_session), redis=Depends(get_redis)):
    original = await get_original_url(short_code, session, redis)
    if not original:
        raise HTTPException(status_code=404, detail="short code not found")
    return RedirectResponse(url=original, status_code=307)


@router.get("/stats/{short_code}", response_model=StatsResponse, dependencies=[Depends(RateLimiter(times=300, seconds=60))])
async def stats(short_code: str, request: Request, session: AsyncSession = Depends(get_session), redis=Depends(get_redis)):
    stats_result = await get_stats(short_code, session, redis)
    if not stats_result:
        raise HTTPException(status_code=404, detail="short code not found")
    return stats_result

@router.get('/urls/{short_code}/visits', dependencies=[Depends(RateLimiter(times=300, seconds=60))])
async def visits(short_code: str, request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, le=100), session: AsyncSession = Depends(get_session)):
    logs = await get_visits_paginated(short_code, session, page, page_size)
    if logs is None:
        raise HTTPException(status_code=404, detail="short code not found")
    return {'page': page, 'page_size': page_size, 'logs': logs}