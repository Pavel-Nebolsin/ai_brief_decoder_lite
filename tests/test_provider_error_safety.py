from httpx import AsyncClient

from app.api.deps import get_provider
from app.main import app
from app.providers import ProviderError


class _LeakyProvider:
    """Test double simulating a provider whose underlying exception text
    would contain sensitive details (auth headers, response bodies, etc.)."""

    async def decode(self, text: str) -> str:
        try:
            raise RuntimeError("Bearer sk-super-secret-token leaked in HTTP body")
        except RuntimeError as exc:
            raise ProviderError("The LLM provider request failed") from exc


async def test_provider_error_never_leaks_raw_exception_text(client: AsyncClient) -> None:
    app.dependency_overrides[get_provider] = lambda: _LeakyProvider()
    try:
        response = await client.post("/v1/briefs/decode", json={"text": "any brief"})
    finally:
        app.dependency_overrides.pop(get_provider, None)

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == "provider_error"
    assert "sk-super-secret-token" not in body["error"]["message"]
    assert body["error"]["message"] == "The LLM provider request failed"
