import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decode_run import DecodeRun
from app.schemas.brief import BriefDecodeResult, DecodeBriefResponse, SafeError


class DecodeRunRepository:
    """Persistence boundary for DecodeRun rows; owns all reads/writes for a decode run."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, input_text: str) -> DecodeRun:
        run = DecodeRun(input_text=input_text)
        self._session.add(run)
        await self._session.commit()
        await self._session.refresh(run)
        return run

    async def get(self, run_id: uuid.UUID) -> DecodeRun | None:
        return await self._session.get(DecodeRun, run_id)

    async def mark_succeeded(self, run_id: uuid.UUID, raw_output: str, result: BriefDecodeResult) -> None:
        run = await self._session.get(DecodeRun, run_id)
        run.status = "succeeded"
        run.raw_provider_output = raw_output
        run.structured_result = result.model_dump(mode="json")
        await self._session.commit()

    async def mark_failed(
        self,
        run_id: uuid.UUID,
        raw_output: str | None,
        error_code: str,
        error_message: str,
    ) -> None:
        run = await self._session.get(DecodeRun, run_id)
        run.status = "failed"
        run.raw_provider_output = raw_output
        run.error_code = error_code
        run.error_message = error_message
        await self._session.commit()

    async def to_response(self, run_id: uuid.UUID) -> DecodeBriefResponse:
        """Load a run and shape it into the public API response schema."""
        run = await self._session.get(DecodeRun, run_id)
        return DecodeBriefResponse(
            run_id=run.id,
            status=run.status,
            result=BriefDecodeResult.model_validate(run.structured_result) if run.structured_result else None,
            error=SafeError(code=run.error_code, message=run.error_message) if run.error_code else None,
            created_at=run.created_at,
        )
