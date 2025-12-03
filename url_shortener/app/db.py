import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings

Base = declarative_base()


DATABASE_URL = settings.DATABASE_URL

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=int(settings.DB_POOL_SIZE),
    max_overflow=int(settings.DB_MAX_OVERFLOW),
    pool_timeout=int(settings.DB_POOL_TIMEOUT),
    future=True,
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=sa.ext.asyncio.AsyncSession)


async def create_tables_if_not_exist():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
