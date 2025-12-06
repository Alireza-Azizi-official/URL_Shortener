import asyncio
import json
from typing import Optional

from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI

from app.config import settings
from app.db import AsyncSessionLocal
from app.log_config import logger
from app.models import URL, VisitLog

KAFKA_ENABLED = settings.KAFKA_ENABLED
KAFKA_BOOTSTRAP = settings.KAFKA_BOOTSTRAP_SERVER
KAFKA_TOPIC = settings.KAFKA_VISIT_TOPIC

consumer: Optional[AIOKafkaConsumer] = None
consumer_task: Optional[asyncio.Task] = None


async def init_kafka_consumer(app: FastAPI):
    global consumer, consumer_task
    if not KAFKA_ENABLED:
        logger.info("kafka is disabled. skipping consumer initialization.")
        return
    logger.info("initializing kafka consumer... ")
    try:
        consumer = AIOKafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id="visit logger group",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await consumer.start()
        logger.info(f"kafka consumer connected at {KAFKA_BOOTSTRAP}")
        consumer_task = asyncio.create_task(consume_loop())
        app.state.kafka_consumer = consumer

    except Exception as e:
        logger.error(f"failed to initialize kafka consumer: {e}", exc_info=True)
        consumer = None


async def consume_loop():
    logger.info("kafka consumer loop started")
    global consumer
    try:
        while True:
            if consumer is None:
                await asyncio.sleep(1)
                continue
            async for msg in consumer:
                event = msg.value
                logger.info(f"received kafka event: {event}")
                await process_visit_event(event)
    except asyncio.CancelledError:
        logger.info("kafka consumer loop cancelled.")
    except Exception as e:
        logger.error(f"kafka consumer loop error: {e}", exc_info=True)


async def process_visit_event(event: dict):
    url_id = event.get("url_id")
    short_code = event.get("short_code")
    ip = event.get("ip")

    if not url_id or not short_code:
        logger.warning(f"invalid visit event received: {event}")
        return
    try:
        async with AsyncSessionLocal() as session:
            visit = VisitLog(
                url_id=url_id,
                ip=ip,
                user_agent="(unknown)",
            )
            session.add(visit)
            await session.execute(
                URL.__table__.update()
                .where(URL.id == url_id)
                .values(visits_count=URL.visits_count + 1)
            )
            await session.commit()
        logger.info(
            f"processed visit event: short_code={short_code}, url_id={url_id}, ip={ip}"
        )
    except Exception as e:
        logger.error(f"failed to process visit event: {e}", exc_info=True)


async def close_kafka_consumer(app: FastAPI):
    global consumer, consumer_task
    if consumer_task:
        consumer_task.cancel()
    try:
        if consumer:
            logger.info("stopping kafka consumer...")
            await consumer.stop()
            logger.info("kafka consumer stopped.")
    except Exception as e:
        logger.error(f"error closing kafka consumer: {e}", exc_info=True)
