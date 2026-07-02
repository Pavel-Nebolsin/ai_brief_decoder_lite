from httpx import AsyncClient

from app.api.deps import get_repository
from app.main import app
from app.repositories.decode_run_repository import PersistenceError


class _BrokenRepository:
    """Test double simulating a database that is unreachable."""

    async def create(self, input_text: str):
        raise PersistenceError("Failed to create decode run")


async def test_database_failure_returns_500_with_generic_message(client: AsyncClient) -> None:
    app.dependency_overrides[get_repository] = lambda: _BrokenRepository()
    try:
        response = await client.post("/v1/briefs/decode", json={"text": "any brief"})
    finally:
        app.dependency_overrides.pop(get_repository, None)

    assert response.status_code == 500
    body = response.json()
    assert body == {"detail": "Internal server error"}
