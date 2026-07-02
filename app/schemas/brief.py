import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    """A single identified risk with its severity and rationale."""

    risk: str
    severity: Literal["low", "medium", "high"]
    reason: str


class BriefDecodeResult(BaseModel):
    """Structured decode output produced by the LLM provider."""

    summary: str
    goals: list[str]
    deliverables: list[str]
    constraints: list[str]
    risks: list[RiskItem]
    clarifying_questions: list[str]
    recommended_next_action: str


class SafeError(BaseModel):
    """Sanitized, client-facing error — never exposes raw provider output or stack traces."""

    code: Literal["invalid_json", "missing_field", "invalid_severity", "provider_error", "timeout"]
    message: str


class DecodeBriefRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)


class DecodeBriefResponse(BaseModel):
    """Public API response shape. `result` and `error` are mutually exclusive based on `status`."""

    run_id: uuid.UUID
    status: Literal["pending", "succeeded", "failed"]
    result: BriefDecodeResult | None = None
    error: SafeError | None = None
    created_at: datetime
