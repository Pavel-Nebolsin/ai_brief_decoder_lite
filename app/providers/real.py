from pydantic_ai import Agent

from app.providers.base import ProviderError
from app.schemas.brief import BriefDecodeResult

_SYSTEM_PROMPT = (
    "You are a project analyst. Given a client brief, extract a structured summary: "
    "the overall summary, goals, deliverables, constraints, risks (each with a "
    "severity of low/medium/high and a reason), clarifying questions, and a "
    "recommended next action."
)


class RealProvider:
    """LLM provider backed by Gemini via pydantic_ai.

    Any exception raised by `agent.run()` (network failure, auth error, rate
    limiting, model refusal, etc.) is caught and wrapped in ProviderError, so
    decode_service only ever has to handle the same failure shape it already
    handles for FakeProvider — it has no knowledge of pydantic_ai internals.

    The Agent is built lazily in __init__ rather than at module import time,
    so importing this module (e.g. transitively via app.api.deps) never
    requires GOOGLE_API_KEY to be set — only actually selecting LLM_PROVIDER=real
    does. This keeps LLM_PROVIDER=fake fully unaffected by this provider's config.
    """

    def __init__(self) -> None:
        self._agent = Agent(
            "google:gemini-2.5-flash",
            output_type=BriefDecodeResult,
            system_prompt=_SYSTEM_PROMPT,
        )

    async def decode(self, text: str) -> str:
        try:
            result = await self._agent.run(text)
        except Exception as exc:
            # exc may carry raw SDK/HTTP details (auth errors can echo request
            # internals) — never forward str(exc) to the client, see ProviderError.
            raise ProviderError("The LLM provider request failed") from exc
        return result.output.model_dump_json()
