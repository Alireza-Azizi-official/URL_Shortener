from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    REDIS_URL: str = Field("redis://localhost:6379/0")
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIEMOUT: int = 30
    APP_HOST: str = "0.0.0.0"
    APP_HOST: int = 8000
    BASE_URL: str = "http://localhost:8000"
    KAFKA_ENABLED: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
