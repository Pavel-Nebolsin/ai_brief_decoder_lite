import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_provider, get_repository
from app.providers import LLMProvider
from app.repositories import DecodeRunRepository
from app.schemas import DecodeBriefRequest, DecodeBriefResponse
from app.services import decode_brief, to_response

router = APIRouter(prefix="/v1/briefs", tags=["briefs"])


@router.post("/decode", response_model=DecodeBriefResponse)
async def decode(
    body: DecodeBriefRequest,
    provider: Annotated[LLMProvider, Depends(get_provider)],
    repo: Annotated[DecodeRunRepository, Depends(get_repository)],
) -> DecodeBriefResponse:
    """Decode a client brief into a structured summary. Always responds with HTTP
    200 — domain failures are reported via `status: "failed"` and `error`, not HTTP status."""
    return await decode_brief(body.text, provider, repo)


@router.get("/runs/{run_id}", response_model=DecodeBriefResponse)
async def get_run(
    run_id: uuid.UUID,
    repo: Annotated[DecodeRunRepository, Depends(get_repository)],
) -> DecodeBriefResponse:
    """Fetch a previously created decode run by id. Returns 404 if the run id
    itself is unknown — a transport-level 404, distinct from a domain decode failure."""
    run = await repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return to_response(run)
