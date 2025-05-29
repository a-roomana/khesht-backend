import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.helper.redis_helper import redis_manager
from app.main import app

__all__ = ["event_loop", "client", "setup_teardown_redis"]


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client():
    await redis_manager.connect()
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c

    await redis_manager.disconnect()

@pytest.fixture(scope="function", autouse=True)
async def setup_teardown_redis():
    keys = await redis_manager.redis_client.keys("*")
    for k in keys:
        await redis_manager.redis_client.delete(k)

    yield

