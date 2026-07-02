import pytest
from pydantic import ValidationError

from app.schemas.brief import BriefDecodeResult, DecodeBriefRequest
from app.services.decode_service import classify_validation_error

VALID_PAYLOAD = {
    "summary": "A short summary",
    "goals": ["Goal one"],
    "deliverables": ["Deliverable one"],
    "constraints": ["Constraint one"],
    "risks": [{"risk": "Some risk", "severity": "medium", "reason": "Some reason"}],
    "clarifying_questions": ["Question one?"],
    "recommended_next_action": "Do the next thing",
}


def test_valid_payload_passes() -> None:
    result = BriefDecodeResult.model_validate(VALID_PAYLOAD)
    assert result.summary == "A short summary"


def test_missing_field_is_classified_correctly() -> None:
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "goals"}
    with pytest.raises(ValidationError) as exc_info:
        BriefDecodeResult.model_validate(payload)
    code, message = classify_validation_error(exc_info.value)
    assert code == "missing_field"
    assert "missing" in message.lower()


def test_invalid_severity_is_classified_correctly() -> None:
    payload = {**VALID_PAYLOAD, "risks": [{**VALID_PAYLOAD["risks"][0], "severity": "critical"}]}
    with pytest.raises(ValidationError) as exc_info:
        BriefDecodeResult.model_validate(payload)
    code, message = classify_validation_error(exc_info.value)
    assert code == "invalid_severity"


def test_wrong_field_type_is_classified_as_missing_field_with_specific_message() -> None:
    payload = {**VALID_PAYLOAD, "goals": "not a list"}
    with pytest.raises(ValidationError) as exc_info:
        BriefDecodeResult.model_validate(payload)
    code, message = classify_validation_error(exc_info.value)
    assert code == "missing_field"
    assert "goals" in message


def test_missing_severity_inside_risk_is_classified_as_missing_field() -> None:
    payload = {**VALID_PAYLOAD, "risks": [{"risk": "r", "reason": "x"}]}
    with pytest.raises(ValidationError) as exc_info:
        BriefDecodeResult.model_validate(payload)
    code, message = classify_validation_error(exc_info.value)
    assert code == "missing_field"


def test_empty_text_request_is_rejected() -> None:
    with pytest.raises(ValidationError):
        DecodeBriefRequest.model_validate({"text": ""})


def test_too_long_text_request_is_rejected() -> None:
    with pytest.raises(ValidationError):
        DecodeBriefRequest.model_validate({"text": "x" * 10_001})
