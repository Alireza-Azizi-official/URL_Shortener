import asyncio

from sqlalchemy import select, update
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.db import AsyncSessionLocal
from app.kafka_producer import publish_visit_event
from app.log_config import logger
from app.models import URL, VisitLog


class VisitLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        result = await call_next(request)

        try:
            SKIP_PATHS = {'docs', 'openapi.json', 'redoc'}
            parts = path.strip("/").split("/")
            if len(parts) == 1 and parts[0] not in SKIP_PATHS:
                short_code = parts[0]
                asyncio.create_task(self._record_visits(request, short_code))
        except Exception as e:
            logger.error(
                f"error scheduling visit recording for path {path}: {e}", exc_info=True
            )

        return result

    async def _record_visits(self, request: Request, short_code: str):
        try:
            async with AsyncSessionLocal() as session:
                q = select(URL.id).where(URL.short_code == short_code)
                res = await session.execute(q)
                row = res.scalar_one_or_none()
                if not row:
                    logger.debug(f"short code not found in DB: {short_code}")
                    return
                url_id = row
                visit = VisitLog(
                    url_id=url_id,
                    ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
                session.add(visit)

                await session.execute(
                    update(URL)
                    .where(URL.id == url_id)
                    .values(visits_count=URL.visits_count + 1)
                )
                await session.commit()
                logger.debug(
                    f"Visit recorded for short_code {short_code}, url_id {url_id}"
                )
                await publish_visit_event(
                    {
                        "url_id": url_id,
                        "short_code": short_code,
                        "ip": request.client.host if request.client else None,
                    }
                )
        except Exception as e:
            logger.error(
                f"failed to record visit for short_code {short_code}: {e}",
                exc_info=True,
            )
