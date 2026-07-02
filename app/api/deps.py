from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db_session
from app.providers import FakeProvider, LLMProvider, RealProvider
from app.repositories import DecodeRunRepository


def get_provider() -> LLMProvider:
    """Resolve the configured LLM provider (FastAPI dependency).

    Only "fake" and "real" are implemented; any other LLM_PROVIDER value is a
    hard configuration error rather than a silent fallback.
    """
    if settings.llm_provider == "fake":
        return FakeProvider()
    if settings.llm_provider == "real":
        return RealProvider()
    raise NotImplementedError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")


def get_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> DecodeRunRepository:
    """Build a DecodeRunRepository bound to the request-scoped DB session (FastAPI dependency)."""
    return DecodeRunRepository(session)
