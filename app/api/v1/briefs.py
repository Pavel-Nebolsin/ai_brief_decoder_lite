import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_provider, get_repository
from app.providers.base import LLMProvider
from app.repositories.decode_run_repository import DecodeRunRepository
from app.schemas.brief import DecodeBriefRequest, DecodeBriefResponse
from app.services.decode_service import decode_brief, to_response

router = APIRouter(prefix="/v1/briefs", tags=["briefs"])


@router.post("/decode", response_model=DecodeBriefResponse)
async def decode(
    body: DecodeBriefRequest,
    provider: Annotated[LLMProvider, Depends(get_provider)],
    repo: Annotated[DecodeRunRepository, Depends(get_repository)],
) -> DecodeBriefResponse:
    """Decode a client brief into a structured summary.

    Always responds with HTTP 200. Domain failures (invalid LLM output, provider
    errors, timeouts) are reported via `status: "failed"` and the `error` field in
    the response body, not via HTTP error status codes — see `decode_brief` for why.
    """
    return await decode_brief(body.text, provider, repo)


@router.get("/runs/{run_id}", response_model=DecodeBriefResponse)
async def get_run(
    run_id: uuid.UUID,
    repo: Annotated[DecodeRunRepository, Depends(get_repository)],
) -> DecodeBriefResponse:
    """Fetch a previously created decode run by id.

    Returns 404 if the run id itself is unknown; this is a transport-level
    "resource not found", distinct from a domain-level decode failure.
    """
    run = await repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return to_response(run)
