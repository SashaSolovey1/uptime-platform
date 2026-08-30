from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.checks.entities import (
    Check,
    CheckResult,
)
from uptime_platform.checks.models import CheckModel


class SqlAlchemyCheckRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        monitor_id: UUID,
        result: CheckResult,
    ) -> Check:
        model = CheckModel(
            monitor_id=monitor_id,
            success=result.success,
            response_time_ms=result.response_time_ms,
            status_code=result.status_code,
            error=result.error,
            checked_at=datetime.now(UTC),
        )

        self._session.add(model)

        await self._session.commit()
        await self._session.refresh(model)

        return self._to_entity(model)

    @staticmethod
    def _to_entity(
        model: CheckModel,
    ) -> Check:
        return Check(
            id=model.id,
            monitor_id=model.monitor_id,
            success=model.success,
            response_time_ms=model.response_time_ms,
            status_code=model.status_code,
            error=model.error,
            checked_at=model.checked_at,
        )

    async def get_by_monitor_id(self, monitor_id: UUID, limit: int) -> list[Check]:
        statement = (
            select(CheckModel)
            .where(CheckModel.monitor_id == monitor_id)
            .order_by(CheckModel.checked_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(statement)

        models = result.scalars().all()

        return [self._to_entity(model) for model in models]
