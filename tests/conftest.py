import asyncio
import pytest
from typing import Generator

import httpx
from tortoise.contrib.test import finalizer, initializer

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(event_loop) -> None:
    initializer(["app.infra.postgres.models"], db_url="sqlite://:memory:")
    yield
    finalizer()


@pytest.fixture(scope="function")
async def client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
