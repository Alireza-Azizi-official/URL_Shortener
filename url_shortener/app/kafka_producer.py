import json
from typing import Optional

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from log_config import logger

from .config import settings

KAFKA_ENABLED = settings.KAFKA_ENABLED
KAFKA_BOOTSTRAP = settings.KAFKA_BOOTSTRAP_SERVER
KAFKA_TOPIC = settings.KAFKA_VISIT_TOPIC


producer: Optional[AIOKafkaProducer] = None


async def init_kafka(app: FastAPI):
    global producer
    if not KAFKA_ENABLED:
        logger.info("kafka is disabled. skipping initialization.")
        return
    logger.info("initializing kafka producer...")
    try:
        producer = AIOKafkaProducer(
            bootstrap_server=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            linger_msg=5,
            acks="all",
        )
        await producer.start()
        app.state.kafka_producer = producer
        logger.info(f"kafka producer connected at {KAFKA_BOOTSTRAP}")

    except Exception as e:
        logger.error(f"failed to initialize kafka: {e}", exc_info=True)
        producer = None


async def close_kafka(app: FastAPI):
    if not producer:
        return
    logger.info("shutting down kafka producer...")
    try:
        await producer.stop()
        logger.info("kafka producer closed.")
    except Exception as e:
        logger.error(f"error closing kafka producer: {e}", exc_info=True)


async def publish_visit_event(event: dict):
    if not KAFKA_ENABLED or not producer:
        logger.debug("kafka disabled. event not sent")
        return
    if not producer:
        logger.warning("kafka producer is not initialized. event not sent.")
        return

    try:
        await producer.send_and_wait(KAFKA_TOPIC, event)
        logger.info(f'published kafka event to "{KAFKA_TOPIC}": {event}')
    except Exception as e:
        logger.error(f"failed to publish kafka event: {e}", exc_info=True)
