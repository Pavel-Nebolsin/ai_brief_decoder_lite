import pytest

from app.providers import ProviderError, RealProvider


def test_construction_does_not_require_google_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    RealProvider()  # must not raise — Agent is built lazily on first decode()


async def test_missing_google_api_key_raises_provider_error_on_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    provider = RealProvider()
    with pytest.raises(ProviderError):
        await provider.decode("some brief")
