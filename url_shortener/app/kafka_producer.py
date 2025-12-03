import asyncio

from app.config import settings

KAFKA_ENABLED = settings.KAFKA_ENABLED


async def publish_visit_events(event: dict):
    if not KAFKA_ENABLED:
        return
    await asyncio.sleep(0)
