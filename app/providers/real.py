from pydantic_ai import Agent

from app.providers.base import ProviderError
from app.schemas import BriefDecodeResult

_SYSTEM_PROMPT = (
    "You are a project analyst. Given a client brief, extract a structured summary: "
    "the overall summary, goals, deliverables, constraints, risks (each with a "
    "severity of low/medium/high and a reason), clarifying questions, and a "
    "recommended next action."
)


class RealProvider:
    """LLM provider backed by Gemini via pydantic_ai. Agent is built lazily, on first
    decode() call, so GOOGLE_API_KEY is only required when LLM_PROVIDER=real is
    actually used — and any misconfiguration surfaces as ProviderError, not a raw
    exception during dependency resolution."""

    def __init__(self) -> None:
        self._agent: Agent | None = None

    def _get_agent(self) -> Agent:
        if self._agent is None:
            try:
                self._agent = Agent(
                    "google:gemini-2.5-flash",
                    output_type=BriefDecodeResult,
                    system_prompt=_SYSTEM_PROMPT,
                )
            except Exception as exc:
                raise ProviderError("The LLM provider is not configured correctly") from exc
        return self._agent

    async def decode(self, text: str) -> str:
        agent = self._get_agent()
        try:
            result = await agent.run(text)
        except Exception as exc:
            # exc may carry raw SDK/HTTP details — never forward str(exc) to the client.
            raise ProviderError("The LLM provider request failed") from exc
        return result.output.model_dump_json()
