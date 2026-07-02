import asyncio
import json

from app.providers.base import ProviderError


def _valid_payload_template(text: str = "") -> dict:
    summary_source = " ".join(text.split()[:8]) or "Untitled brief"
    return {
        "summary": f"Brief about: {summary_source}",
        "goals": ["Deliver the requested output on time"],
        "deliverables": ["Final artifact matching the brief"],
        "constraints": ["Limited budget or timeline"],
        "risks": [
            {
                "risk": "Requirements may be incomplete",
                "severity": "medium",
                "reason": "The brief does not specify all details needed to start work",
            },
            {
                "risk": "Scope creep",
                "severity": "high",
                "reason": "No clear boundaries were defined for what is out of scope",
            },
            {
                "risk": "Minor terminology ambiguity",
                "severity": "low",
                "reason": "Some terms in the brief could be interpreted in more than one way",
            },
        ],
        "clarifying_questions": ["What is the target deadline?"],
        "recommended_next_action": "Schedule a kickoff call to clarify scope",
    }


class FakeProvider:
    """Deterministic stand-in for a real LLM provider.

    Failure modes are triggered by literal markers in the input text rather than
    randomly, so that tests and manual QA can reproduce any specific failure branch
    (invalid JSON, missing field, bad severity, provider error, timeout) on demand
    instead of relying on flaky chance.
    """

    async def decode(self, text: str) -> str:
        if "__FAKE_INVALID_JSON__" in text:
            return "{not valid json"
        if "__FAKE_MISSING_FIELD__" in text:
            return json.dumps({"summary": "...", "goals": []})
        if "__FAKE_INVALID_SEVERITY__" in text:
            payload = _valid_payload_template(text)
            payload["risks"][0]["severity"] = "critical"
            return json.dumps(payload)
        if "__FAKE_PROVIDER_ERROR__" in text:
            raise ProviderError("simulated upstream failure")
        if "__FAKE_TIMEOUT__" in text:
            await asyncio.sleep(3600)
        return json.dumps(_valid_payload_template(text))
