import asyncio
import json

from pydantic import ValidationError

from app.config import settings
from app.providers.base import LLMProvider, ProviderError
from app.repositories.decode_run_repository import DecodeRunRepository
from app.schemas.brief import BriefDecodeResult, DecodeBriefResponse


def classify_validation_error(exc: ValidationError) -> tuple[str, str]:
    """Map a Pydantic ValidationError to a (SafeError code, message) pair. Invalid
    severity checked first as the more specific diagnosis; anything else (missing
    or wrong-type fields) maps to `missing_field`, with a message naming the field."""
    for error in exc.errors():
        loc = error["loc"]
        if error["type"] == "literal_error" and len(loc) >= 1 and loc[-1] == "severity":
            return "invalid_severity", "LLM returned severity outside low/medium/high"

    for error in exc.errors():
        if error["type"] != "missing":
            loc = ".".join(str(part) for part in error["loc"])
            return "missing_field", f"LLM output has an invalid value for field: {loc}"

    return "missing_field", "LLM output is missing one or more required fields"


async def decode_brief(text: str, provider: LLMProvider, repo: DecodeRunRepository) -> DecodeBriefResponse:
    """Run a brief through the LLM provider and persist the outcome. Domain failures
    (timeout, provider error, invalid output) are recorded as `status: "failed"`,
    never raised. PersistenceError (DB failure) is NOT caught here — it propagates
    to the API layer as HTTP 500, since there's no run to report back for."""
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
        code, message = classify_validation_error(exc)
        return await fail(code, message, raw_output=raw_output)

    await repo.mark_succeeded(run.id, raw_output=raw_output, result=result)
    return await repo.to_response(run.id)
