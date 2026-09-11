from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.incidents.entities import (
    Incident,
    IncidentStatus,
)
from uptime_platform.incidents.models import IncidentModel


class SqlAlchemyIncidentRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        incident: Incident,
    ) -> Incident:
        model = IncidentModel(
            id=incident.id,
            monitor_id=incident.monitor_id,
            status=incident.status,
            started_at=incident.started_at,
            resolved_at=incident.resolved_at,
        )

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(
        self,
        incident_id: UUID,
    ) -> Incident | None:
        model = await self._session.get(
            IncidentModel,
            incident_id,
        )

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all(
        self,
        status: IncidentStatus | None,
        monitor_ids: set[UUID],
        limit: int,
    ) -> list[Incident]:
        if not monitor_ids:
            return []

        statement = select(IncidentModel).where(
            IncidentModel.monitor_id.in_(monitor_ids)
        )

        if status is not None:
            statement = statement.where(IncidentModel.status == status)

        statement = statement.order_by(IncidentModel.started_at.desc()).limit(limit)

        result = await self._session.execute(statement)

        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_open_by_monitor_id(
        self,
        monitor_id: UUID,
    ) -> Incident | None:
        statement = select(IncidentModel).where(
            IncidentModel.monitor_id == monitor_id,
            IncidentModel.status == IncidentStatus.OPEN,
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(
        self,
        incident: Incident,
    ) -> Incident | None:
        model = await self._session.get(
            IncidentModel,
            incident.id,
        )

        if model is None:
            return None

        model.status = incident.status
        model.resolved_at = incident.resolved_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_monitor_id(
        self,
        monitor_id: UUID,
        limit: int,
    ) -> list[Incident]:
        statement = (
            select(IncidentModel)
            .where(IncidentModel.monitor_id == monitor_id)
            .order_by(IncidentModel.started_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(statement)

        return [self._to_entity(model) for model in result.scalars().all()]

    @staticmethod
    def _to_entity(
        model: IncidentModel,
    ) -> Incident:
        return Incident(
            id=model.id,
            monitor_id=model.monitor_id,
            status=model.status,
            started_at=model.started_at,
            resolved_at=model.resolved_at,
        )
