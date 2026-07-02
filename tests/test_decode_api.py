import pytest
from httpx import AsyncClient

from app.config import settings


async def test_decode_happy_path(client: AsyncClient) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": "We need a landing page for a SaaS product"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "succeeded"
    assert body["error"] is None
    assert body["result"]["risks"][0]["severity"] in ("low", "medium", "high")


async def test_decode_invalid_json_marker(client: AsyncClient) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": "__FAKE_INVALID_JSON__ brief"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["result"] is None
    assert body["error"]["code"] == "invalid_json"


async def test_decode_missing_field_marker(client: AsyncClient) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": "__FAKE_MISSING_FIELD__ brief"})
    assert response.status_code == 200
    assert response.json()["error"]["code"] == "missing_field"


async def test_decode_invalid_severity_marker(client: AsyncClient) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": "__FAKE_INVALID_SEVERITY__ brief"})
    assert response.status_code == 200
    assert response.json()["error"]["code"] == "invalid_severity"


async def test_decode_provider_error_marker(client: AsyncClient) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": "__FAKE_PROVIDER_ERROR__ brief"})
    assert response.status_code == 200
    assert response.json()["error"]["code"] == "provider_error"


async def test_decode_empty_text_returns_422(client: AsyncClient) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": ""})
    assert response.status_code == 422


async def test_decode_timeout_marker(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_timeout_seconds", 0.05)
    response = await client.post("/v1/briefs/decode", json={"text": "__FAKE_TIMEOUT__ brief"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["result"] is None
    assert body["error"]["code"] == "timeout"
