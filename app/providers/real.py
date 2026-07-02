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
    """LLM provider backed by Gemini via pydantic_ai. Agent is built lazily so
    GOOGLE_API_KEY is only required when LLM_PROVIDER=real is actually selected."""

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
            # exc may carry raw SDK/HTTP details — never forward str(exc) to the client.
            raise ProviderError("The LLM provider request failed") from exc
        return result.output.model_dump_json()
