from typing import Protocol


class ProviderError(Exception):
    """Domain-level LLM provider failure. `safe_message` is safe to show to clients."""

    def __init__(self, safe_message: str) -> None:
        super().__init__(safe_message)
        self.safe_message = safe_message


class LLMProvider(Protocol):
    """Structural interface every LLM provider (fake or real) must satisfy."""

    async def decode(self, text: str) -> str: ...
