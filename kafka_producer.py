import json
from typing import Optional

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI

from .config import settings

KAFKA_ENABLED = settings.KAFKA_ENABLED
KAFKA_BOOTSTRAP = settings.KAFKA_BOOTSTRAP_SERVERS
KAFKA_TOPIC = settings.KAFKA_VISIT_TOPIC


producer = Optional[AIOKafkaProducer] = None


async def init_kafka(app: FastAPI):
    global producer
    if not KAFKA_ENABLED:
        return

    producer = AIOKafkaProducer(
        bootstrap_server=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_msg=5,
        acks="all",
    )
    await producer.start()
    app.state.kafka_producer = producer


async def close_kafka(app: FastAPI):
    if producer:
        await producer.stop()


async def publish_visit_event(event: dict):
    if not KAFKA_ENABLED or not producer:
        return

    try:
        await producer.send_and_wait(KAFKA_TOPIC, event)
    except Exception as e:
        print(f"[KAFKA EROR] {str(e)}")
