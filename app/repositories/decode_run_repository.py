import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DecodeRun
from app.schemas import BriefDecodeResult


class PersistenceError(Exception):
    """Raised when a decode run can't be read or written due to a database failure.
    An infrastructure problem, distinct from ProviderError's domain outcomes."""


class DecodeRunRepository:
    """Persistence boundary for DecodeRun rows; owns all reads/writes for a decode run."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, input_text: str) -> DecodeRun:
        try:
            run = DecodeRun(input_text=input_text)
            self._session.add(run)
            await self._session.commit()
            await self._session.refresh(run)
            return run
        except SQLAlchemyError as exc:
            raise PersistenceError("Failed to create decode run") from exc

    async def get(self, run_id: uuid.UUID) -> DecodeRun | None:
        try:
            return await self._session.get(DecodeRun, run_id)
        except SQLAlchemyError as exc:
            raise PersistenceError("Failed to fetch decode run") from exc

    async def mark_succeeded(self, run: DecodeRun, raw_output: str, result: BriefDecodeResult) -> DecodeRun:
        try:
            run.status = "succeeded"
            run.raw_provider_output = raw_output
            run.structured_result = result.model_dump(mode="json")
            await self._session.commit()
            await self._session.refresh(run)
            return run
        except SQLAlchemyError as exc:
            raise PersistenceError("Failed to record successful decode run") from exc

    async def mark_failed(
        self,
        run: DecodeRun,
        raw_output: str | None,
        error_code: str,
        error_message: str,
    ) -> DecodeRun:
        try:
            run.status = "failed"
            run.raw_provider_output = raw_output
            run.error_code = error_code
            run.error_message = error_message
            await self._session.commit()
            await self._session.refresh(run)
            return run
        except SQLAlchemyError as exc:
            raise PersistenceError("Failed to record failed decode run") from exc
