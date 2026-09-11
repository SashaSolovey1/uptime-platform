from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.maintenance.entities import (
    MaintenanceWindow,
)
from uptime_platform.maintenance.models import (
    MaintenanceWindowModel,
)


class SqlAlchemyMaintenanceWindowRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        window: MaintenanceWindow,
    ) -> MaintenanceWindow:
        model = MaintenanceWindowModel(
            id=window.id,
            monitor_id=window.monitor_id,
            starts_at=window.starts_at,
            ends_at=window.ends_at,
            reason=window.reason,
            created_at=window.created_at,
        )

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(
        self,
        window_id: UUID,
    ) -> MaintenanceWindow | None:
        model = await self._session.get(
            MaintenanceWindowModel,
            window_id,
        )

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all(
        self,
        monitor_ids: set[UUID],
    ) -> list[MaintenanceWindow]:
        if not monitor_ids:
            return []

        statement = (
            select(MaintenanceWindowModel)
            .where(MaintenanceWindowModel.monitor_id.in_(monitor_ids))
            .order_by(MaintenanceWindowModel.starts_at.desc())
        )

        result = await self._session.execute(statement)

        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_active(
        self,
        monitor_id: UUID,
        now: datetime,
    ) -> MaintenanceWindow | None:
        statement = (
            select(MaintenanceWindowModel)
            .where(
                MaintenanceWindowModel.monitor_id == monitor_id,
                MaintenanceWindowModel.starts_at <= now,
                MaintenanceWindowModel.ends_at > now,
            )
            .order_by(MaintenanceWindowModel.starts_at.desc())
            .limit(1)
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def delete(
        self,
        window_id: UUID,
    ) -> bool:
        model = await self._session.get(
            MaintenanceWindowModel,
            window_id,
        )

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()

        return True

    @staticmethod
    def _to_entity(
        model: MaintenanceWindowModel,
    ) -> MaintenanceWindow:
        return MaintenanceWindow(
            id=model.id,
            monitor_id=model.monitor_id,
            starts_at=model.starts_at,
            ends_at=model.ends_at,
            reason=model.reason,
            created_at=model.created_at,
        )
