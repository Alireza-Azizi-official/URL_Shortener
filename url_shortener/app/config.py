from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    BASE_URL: str = "http://localhost:8000"
    KAFKA_ENABLED: bool = False
    KAFKA_BOOTSTRAP_SERVER: str = 'localhost:9092'
    KAFKA_VISIT_TOPIC: str = 'visit_events'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
