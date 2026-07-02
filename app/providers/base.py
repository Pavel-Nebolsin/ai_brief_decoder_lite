from typing import Protocol


class ProviderError(Exception):
    """Raised when an LLM provider fails in a way that maps to a domain error, not a bug.

    `safe_message` is what SafeError.message will show to the client — it must
    never contain raw SDK/HTTP exception text (auth headers, response bodies,
    internal URLs). The full exception is still chained via `from exc` at the
    raise site for local debugging, but only `safe_message` crosses the API boundary.
    """

    def __init__(self, safe_message: str) -> None:
        super().__init__(safe_message)
        self.safe_message = safe_message


class LLMProvider(Protocol):
    """Structural interface every LLM provider (fake or real) must satisfy."""

    async def decode(self, text: str) -> str: ...
