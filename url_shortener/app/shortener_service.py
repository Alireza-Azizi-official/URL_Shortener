from app.config import settings
from app.models import URL
from app.utils import encode_base62
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

URL_KEY = "url:{}"
COUNT_KEY = "count:{}"


async def create_short_url(original_url: str, session: AsyncSession, redis):
    if not isinstance(original_url, str):
        original_url = str(original_url)

    new_url = URL(original_url=original_url, short_code="temp")
    session.add(new_url)
    await session.flush()


    new_url.short_code = encode_base62(new_url.id)
    await session.commit()


    await redis.set(URL_KEY.format(new_url.short_code), new_url.original_url)
    await redis.set(COUNT_KEY.format(new_url.short_code), 0)

    short_url = f"{settings.BASE_URL.rstrip('/')}/{new_url.short_code}"
    return {"short_code": new_url.short_code, "short_url": short_url}



async def get_original_url(short_code: str, session: AsyncSession, redis):
    cached_url = await redis.get(URL_KEY.format(short_code))
    if cached_url:
        await redis.incr(COUNT_KEY.format(short_code))
        return cached_url

    q = select(URL).where(URL.short_code == short_code)
    res = await session.execute(q)
    url_obj = res.scalar_one_or_none()
    if not url_obj:
        return None

    await redis.set(URL_KEY.format(short_code), url_obj.original_url)
    await redis.set(COUNT_KEY.format(short_code), url_obj.visits_count)

    await session.execute(
        update(URL)
        .where(URL.id == url_obj.id)
        .values(visits_count=url_obj.visits_count + 1)
    )
    await session.commit()

    return url_obj.original_url


async def get_stats(short_code: str, session: AsyncSession, redis):
    cached_count = await redis.get(COUNT_KEY.format(short_code))

    q = select(URL).where(URL.short_code == short_code)
    res = await session.execute(q)
    url_obj = res.scalar_one_or_none()
    if not url_obj:
        return None

    visits = int(cached_count) if cached_count is not None else url_obj.visits_count
    if cached_count is None:
        await redis.set(COUNT_KEY.format(short_code), url_obj.visits_count)

    return {
        "short_code": short_code,
        "original_url": url_obj.original_url,
        "created_at": url_obj.created_at,
        "visits_count": visits,
    }
