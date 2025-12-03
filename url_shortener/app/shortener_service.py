from app.config import settings
from app.models import URL
from app.utils import encode_base62
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

URL_KEY = "url:{}"
COUNT_KEY = "count:{}"


async def create_short_url(original_url: str, session: AsyncSession, redis):
    new = URL(original_url=original_url)
    session.add(new)

    await session.flush()
    if not new.id:
        await session.rollback()
        raise Exception("cannot create")

    short_code = encode_base62(new.id)
    new.short_code = short_code
    session.add(new)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        new.short_code = short_code
        session.add(new)
        await session.commit()

    await redis.set(URL_KEY.format(short_code), new.original_url)
    await redis.set(COUNT_KEY.format(short_code), 0)

    short_url = f"{settings.BASE_URL.rstrip('/')}/{short_code}"

    return {"short_code": short_code, "short_url": short_url}


async def get_original_url(short_code: str, session: AsyncSession, redis):
    cached = await redis.get(URL_KEY.format(short_code))
    if cached:
        await redis.incr(COUNT_KEY.format(short_code))
        return cached

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
        .values(visits_count=URL.visits_count + 1)
    )
    await session.commit()

    return url_obj.original_url


async def get_stats(short_code: str, session: AsyncSession, redis):
    count = await redis.get(COUNT_KEY.format(short_code))

    q = select(URL).where(URL.short_code == short_code)
    res = await session.execute(q)
    url_obj = res.scalar_one_or_none()

    if not url_obj:
        return None

    if count is None:
        await redis.set(COUNT_KEY.format(short_code), url_obj.visits_count)
        visits = url_obj.visits_count
    else:
        visits = int(count)

    return {
        "short_code": short_code,
        "original_url": url_obj.original_url,
        "created_at": url_obj.created_at,
        "visits_count": visits,
    }
