import typing

from aioredis import Redis, from_url
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.models import URL
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.utils import encode_base62

router = APIRouter()


_redis: typing.Optional[Redis] = None


async def get_redis():
    global _redis
    if _redis is None:
        _redis = await from_url(
            settings.REDIS_URL, encoding="utf-8", decode_response=True
        )
    return _redis


@router.post("/shorten", response_model=ShortenResponse)
async def shorten(payload: ShortenRequest, session: AsyncSession = Depends(get_session)):
    new = URL(original_url=str(payload.url))
    session.add(new)
    try:
        await session.flush()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="db error")
    if not new.id:
        await session.rollback()
        raise HTTPException(status_code=500, detail="cannot create")

    short_code = encode_base62(new.id)
    new.short_code = short_code
    session.add(new)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        new.short_code = f"{short_code}"
        session.add(new)
        await session.commit()
    short_url = f"{settings.BASE_URL.rstrip('/')}/{short_code}"
    redis = await get_redis()
    await redis.set(f"url: {short_code}", new.original_url)
    await redis.set(f"count: {short_code}", 0)
    return ShortenResponse(short_code=short_code, short_url=short_url)


@router.get("/{short_code}")
async def redirect_short(short_code: str, request: Request, session: AsyncSession = Depends(get_session)):
    redis = await get_redis()
    original = await redis.get(f"url: {short_code}")
    if original:
        await redis.incr(f"count: {short_code}")
        return RedirectResponse(url=original, status_code=307)
    q = select(URL).where(URL.short_code == short_code)
    res = await session.execute(q)
    url_obj = res.scalar_one_or_none()
    if not url_obj:
        raise HTTPException(status_code=404, detail="short code not found")
    await redis.set(f"url: {short_code}", url_obj.original_url)
    await redis.set(f"count: {short_code}", url_obj.visits_count)
    await session.execute(
        update(URL)
        .where(URL.id == url_obj.id)
        .values(visits_count=URL.visits_count + 1)
    )
    await session.commit()
    return RedirectResponse(url=url_obj.original_url, status_code=307)


@router.get("/stats/{short_code}", response_model=StatsResponse)
async def stats(short_code: str, session: AsyncSession = Depends(get_session)):
    redis = await get_redis()
    count = await redis.get(f"count: {short_code}")
    q = select(URL).where(URL.short_code == short_code)
    res = await session.execute(q)
    url_obj = res.scalar_one_or_none()
    if not url_obj:
        raise HTTPException(status_code=404, detail="short code not found")
    if count is None:
        await redis.set(f"count: {short_code}", url_obj.visits_count)
        visits_count = url_obj.visits_count
    else:
        visits_count = int(count)
    return StatsResponse(
        short_code=short_code,
        original_url=url_obj.original_url,
        created_at=url_obj.created_at,
        visits_count=visits_count,
    )
