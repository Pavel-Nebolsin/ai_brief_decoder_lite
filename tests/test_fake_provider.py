import asyncio
import json

import pytest

from app.providers import FakeProvider, ProviderError


@pytest.fixture
def provider() -> FakeProvider:
    return FakeProvider()


async def test_happy_path_returns_valid_json(provider: FakeProvider) -> None:
    raw = await provider.decode("We need a landing page for a B2B SaaS product")
    parsed = json.loads(raw)
    assert parsed["risks"][0]["severity"] in ("low", "medium", "high")
    assert "landing page" in parsed["summary"]


async def test_invalid_json_marker(provider: FakeProvider) -> None:
    raw = await provider.decode("__FAKE_INVALID_JSON__ some brief")
    with pytest.raises(json.JSONDecodeError):
        json.loads(raw)


async def test_missing_field_marker(provider: FakeProvider) -> None:
    raw = await provider.decode("__FAKE_MISSING_FIELD__ some brief")
    parsed = json.loads(raw)
    assert "risks" not in parsed


async def test_invalid_severity_marker(provider: FakeProvider) -> None:
    raw = await provider.decode("__FAKE_INVALID_SEVERITY__ some brief")
    parsed = json.loads(raw)
    assert parsed["risks"][0]["severity"] == "critical"


async def test_provider_error_marker(provider: FakeProvider) -> None:
    with pytest.raises(ProviderError):
        await provider.decode("__FAKE_PROVIDER_ERROR__ some brief")


async def test_timeout_marker(provider: FakeProvider) -> None:
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(provider.decode("__FAKE_TIMEOUT__ some brief"), timeout=0.05)
