from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.status_pages.entities import (
    StatusPage,
    StatusPageMonitor,
)
from uptime_platform.status_pages.models import (
    StatusPageModel,
    StatusPageMonitorModel,
)


class SqlAlchemyStatusPageRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        page: StatusPage,
    ) -> StatusPage:
        model = StatusPageModel(
            id=page.id,
            name=page.name,
            slug=page.slug,
            published=page.published,
            created_at=page.created_at,
        )

        self._session.add(model)

        await self._session.flush()

        return self._to_entity(model)

    async def get_by_id(
        self,
        page_id: UUID,
    ) -> StatusPage | None:
        model = await self._session.get(
            StatusPageModel,
            page_id,
        )

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_slug(
        self,
        slug: str,
    ) -> StatusPage | None:
        statement = select(StatusPageModel).where(StatusPageModel.slug == slug)

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all(
        self,
    ) -> list[StatusPage]:
        statement = select(StatusPageModel).order_by(StatusPageModel.created_at.desc())

        result = await self._session.execute(statement)

        return [self._to_entity(model) for model in result.scalars().all()]

    async def update(
        self,
        page: StatusPage,
    ) -> StatusPage | None:
        model = await self._session.get(
            StatusPageModel,
            page.id,
        )

        if model is None:
            return None

        model.name = page.name
        model.published = page.published

        await self._session.flush()

        return self._to_entity(model)

    async def delete(
        self,
        page_id: UUID,
    ) -> bool:
        model = await self._session.get(
            StatusPageModel,
            page_id,
        )

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()

        return True

    async def add_monitor(
        self,
        relation: StatusPageMonitor,
    ) -> bool:
        statement = (
            insert(StatusPageMonitorModel)
            .values(
                status_page_id=relation.status_page_id,
                monitor_id=relation.monitor_id,
                position=relation.position,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    StatusPageMonitorModel.status_page_id,
                    StatusPageMonitorModel.monitor_id,
                ]
            )
            .returning(StatusPageMonitorModel.monitor_id)
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none() is not None

    async def remove_monitor(
        self,
        page_id: UUID,
        monitor_id: UUID,
    ) -> bool:
        model = await self._session.get(
            StatusPageMonitorModel,
            {
                "status_page_id": page_id,
                "monitor_id": monitor_id,
            },
        )

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()

        return True

    async def get_monitors(
        self,
        page_id: UUID,
    ) -> list[StatusPageMonitor]:
        statement = (
            select(StatusPageMonitorModel)
            .where(StatusPageMonitorModel.status_page_id == page_id)
            .order_by(
                StatusPageMonitorModel.position,
                StatusPageMonitorModel.monitor_id,
            )
        )

        result = await self._session.execute(statement)

        return [self._relation_to_entity(model) for model in result.scalars().all()]

    @staticmethod
    def _to_entity(
        model: StatusPageModel,
    ) -> StatusPage:
        return StatusPage(
            id=model.id,
            name=model.name,
            slug=model.slug,
            published=model.published,
            created_at=model.created_at,
        )

    @staticmethod
    def _relation_to_entity(
        model: StatusPageMonitorModel,
    ) -> StatusPageMonitor:
        return StatusPageMonitor(
            status_page_id=model.status_page_id,
            monitor_id=model.monitor_id,
            position=model.position,
        )
