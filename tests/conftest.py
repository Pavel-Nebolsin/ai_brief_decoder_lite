from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_provider
from app.main import app
from app.providers import FakeProvider


@pytest.fixture(autouse=True)
def override_provider() -> AsyncIterator[None]:
    app.dependency_overrides[get_provider] = lambda: FakeProvider()
    yield
    app.dependency_overrides.pop(get_provider, None)


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
