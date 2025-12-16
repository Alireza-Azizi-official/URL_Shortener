from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    BASE_URL: str = "http://127.0.0.1:8000"
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
