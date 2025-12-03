from datetime import datetime

from pydantic import AnyUrl, BaseModel


class ShortenRequest(BaseModel):
    url: AnyUrl


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str


class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    visits_count: int
