import asyncio
import json

from pydantic import ValidationError

from app.config import settings
from app.providers.base import LLMProvider, ProviderError
from app.repositories.decode_run_repository import DecodeRunRepository
from app.schemas.brief import BriefDecodeResult, DecodeBriefResponse


def classify_validation_error(exc: ValidationError) -> str:
    """Map a Pydantic ValidationError to a SafeError code. Checks severity first — it's
    the more specific and actionable diagnosis when both errors are present."""
    errors = exc.errors()
    for error in errors:
        if error["loc"][-1] == "severity" and error["type"] in ("literal_error", "enum"):
            return "invalid_severity"
    return "missing_field"


def _error_message(error_code: str) -> str:
    messages = {
        "invalid_severity": "LLM returned severity outside low/medium/high",
        "missing_field": "LLM output is missing one or more required fields",
    }
    return messages[error_code]


async def decode_brief(text: str, provider: LLMProvider, repo: DecodeRunRepository) -> DecodeBriefResponse:
    """Run a brief through the LLM provider and persist the outcome. Domain failures
    (timeout, provider error, invalid output) are recorded as `status: "failed"`,
    never raised — the response is always a normal DecodeBriefResponse."""
    run = await repo.create(input_text=text)

    async def fail(error_code: str, error_message: str, raw_output: str | None) -> DecodeBriefResponse:
        await repo.mark_failed(run.id, raw_output=raw_output, error_code=error_code, error_message=error_message)
        return await repo.to_response(run.id)

    try:
        raw_output = await asyncio.wait_for(provider.decode(text), timeout=settings.llm_timeout_seconds)
    except asyncio.TimeoutError:
        return await fail("timeout", "LLM provider timed out", raw_output=None)
    except ProviderError as exc:
        return await fail("provider_error", exc.safe_message, raw_output=None)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        return await fail("invalid_json", "Provider did not return valid JSON", raw_output=raw_output)

    try:
        result = BriefDecodeResult.model_validate(parsed)
    except ValidationError as exc:
        code = classify_validation_error(exc)
        return await fail(code, _error_message(code), raw_output=raw_output)

    await repo.mark_succeeded(run.id, raw_output=raw_output, result=result)
    return await repo.to_response(run.id)
