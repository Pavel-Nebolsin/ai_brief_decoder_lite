import asyncio
import json

from pydantic import ValidationError

from app.config import settings
from app.models import DecodeRun
from app.providers import LLMProvider, ProviderError
from app.repositories import DecodeRunRepository
from app.schemas import BriefDecodeResult, DecodeBriefResponse, SafeError


def classify_validation_error(exc: ValidationError) -> tuple[str, str]:
    """Map a Pydantic ValidationError to a (SafeError code, message) pair. Invalid
    severity is checked first as the more specific diagnosis."""
    for error in exc.errors():
        loc = error["loc"]
        if error["type"] == "literal_error" and len(loc) >= 1 and loc[-1] == "severity":
            return "invalid_severity", "LLM returned severity outside low/medium/high"

    for error in exc.errors():
        if error["type"] != "missing":
            loc = ".".join(str(part) for part in error["loc"])
            return "missing_field", f"LLM output has an invalid value for field: {loc}"

    return "missing_field", "LLM output is missing one or more required fields"


def to_response(run: DecodeRun) -> DecodeBriefResponse:
    """Shape a persisted DecodeRun into the public API response schema."""
    return DecodeBriefResponse(
        run_id=run.id,
        status=run.status,
        result=BriefDecodeResult.model_validate(run.structured_result) if run.structured_result else None,
        error=SafeError(code=run.error_code, message=run.error_message) if run.error_code else None,
        created_at=run.created_at,
    )


async def decode_brief(text: str, provider: LLMProvider, repo: DecodeRunRepository) -> DecodeBriefResponse:
    """Run a brief through the LLM provider and persist the outcome. Domain failures
    are recorded as `status: "failed"`; PersistenceError propagates as HTTP 500."""
    run = await repo.create(input_text=text)

    async def fail(error_code: str, error_message: str, raw_output: str | None) -> DecodeBriefResponse:
        updated = await repo.mark_failed(run, raw_output=raw_output, error_code=error_code, error_message=error_message)
        return to_response(updated)

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
        code, message = classify_validation_error(exc)
        return await fail(code, message, raw_output=raw_output)

    updated = await repo.mark_succeeded(run, raw_output=raw_output, result=result)
    return to_response(updated)
