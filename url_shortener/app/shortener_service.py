from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .log_config import logger
from .models import URL, VisitLog
from .utils import encode_base62

URL_KEY = "url:{}"
COUNT_KEY = "count:{}"


async def create_short_url(original_url: str, session: AsyncSession, redis):
    logger.info(f"request to shorten url: {original_url}")
    if not isinstance(original_url, str):
        original_url = str(original_url)

    q = select(URL).where(URL.original_url == original_url)
    res = await session.execute(q)
    existing_url = res.scalar_one_or_none()
    if existing_url:
        logger.warning(f"url already exists: {original_url}")
        raise HTTPException(status_code=400, detail="URL already exists")

    new_url = URL(original_url=original_url, short_code="temp")
    session.add(new_url)
    await session.flush()

    new_url.short_code = encode_base62(new_url.id)
    await session.commit()
    logger.info(f"created short code {new_url.short_code} for url: {original_url}")

    await redis.set(URL_KEY.format(new_url.short_code), new_url.original_url)
    await redis.set(COUNT_KEY.format(new_url.short_code), 0)

    short_url = f"{settings.BASE_URL.rstrip('/')}/{new_url.short_code}"
    logger.info(f"short url ready: {short_url}")
    return {"short_code": new_url.short_code, "short_url": short_url}


async def get_original_url(short_code: str, session: AsyncSession, redis):
    logger.info(f"looking up short code: {short_code}")
    cached_url = await redis.get(URL_KEY.format(short_code))
    if cached_url:
        logger.info(f"cache hit for short code {short_code}")
        await redis.incr(COUNT_KEY.format(short_code))
        return cached_url
    logger.info(f"cache miss for short code {short_code}, checking database")

    q = select(URL).where(URL.short_code == short_code)
    res = await session.execute(q)
    url_obj = res.scalar_one_or_none()
    if not url_obj:
        logger.warning(f"short code not found: {short_code}")
        return None
    logger.info(
        f"found url in database for short code {short_code}: {url_obj.original_url}"
    )

    await redis.set(URL_KEY.format(short_code), url_obj.original_url)
    await redis.set(COUNT_KEY.format(short_code), url_obj.visits_count)

    await session.execute(
        update(URL)
        .where(URL.id == url_obj.id)
        .values(visits_count=url_obj.visits_count + 1)
    )
    await session.commit()
    logger.info(f"updated visit count for: {short_code}")

    return url_obj.original_url


async def get_stats(short_code: str, session: AsyncSession, redis):
    logger.info(f"fetching stats for short_code: {short_code}")
    cached_count = await redis.get(COUNT_KEY.format(short_code))

    q = select(URL).where(URL.short_code == short_code)
    res = await session.execute(q)
    url_obj = res.scalar_one_or_none()
    if not url_obj:
        logger.warning(f"stats requested for none-existing short code: {short_code}")
        return None

    visits = int(cached_count) if cached_count is not None else url_obj.visits_count
    if cached_count is None:
        await redis.set(COUNT_KEY.format(short_code), url_obj.visits_count)
    logger.info(
        f"Stats for {short_code}: URL={url_obj.original_url}, "
        f"created_at={url_obj.created_at}, visits={visits}"
    )

    return {
        "short_code": short_code,
        "original_url": url_obj.original_url,
        "created_at": url_obj.created_at,
        "visits_count": visits,
    }


async def get_visits_paginated(short_code: str, session: AsyncSession, page: int = 1, page_size: int = 20):
    q_url = select(URL).where(URL.short_code == short_code)
    res = await session.execute(q_url)
    url_obj = res.scalar_one_or_none()
    if not url_obj:
        return []

    q_logs = (
        select(VisitLog)
        .where(VisitLog.url_id == url_obj.id)
        .order_by(VisitLog.timestamp.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    res_logs = await session.execute(q_logs)
    return res_logs.scalars().all()
