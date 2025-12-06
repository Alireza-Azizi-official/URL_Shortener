import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from app.main import app

REDIS_URL = os.getenv("REDIS_URL")
limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
