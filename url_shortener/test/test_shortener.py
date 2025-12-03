import pytest
from app.db import Base
from app.main import app
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def prepare_db():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture
async def client(prepare_db):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.anyio
async def test_shorten_and_redirect_and_stats(client):
    resp = await client.post("/shorten", json={"url": "https://example.com/path"})
    assert resp.status_code == 200
    data = resp.json()
    assert "short_code" in data
    short_code = data["short_code"]

    resp_stats = await client.get(f"/stats/{short_code}")
    assert resp_stats.status_code == 200
    sdata = resp_stats.json()
    assert sdata["visits_count"] == 0

    resp_redirect = await client.get(f"/{short_code}", follow_redirects=False)
    assert resp_redirect.status_code in (301, 302, 307)
    assert resp_redirect.headers["location"] == "https://example.com/path"

    resp_stats2 = await client.get(f"/stats/{short_code}")
    assert resp_stats2.status_code == 200
    sdata2 = resp_stats2.json()
    assert sdata2["visits_count"] >= 1
