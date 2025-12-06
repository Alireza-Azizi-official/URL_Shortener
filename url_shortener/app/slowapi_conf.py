import os

from slowapi import Limiter

REDIS_URL = os.getenv("REDIS_URL")
limiter = Limiter(key_func=lambda request: request.client.host, storage_uri=REDIS_URL)
