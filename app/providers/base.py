from typing import Protocol


class ProviderError(Exception):
    """Raised when an LLM provider fails in a way that maps to a domain error, not a bug."""


class LLMProvider(Protocol):
    """Structural interface every LLM provider (fake or real) must satisfy."""

    async def decode(self, text: str) -> str: ...
