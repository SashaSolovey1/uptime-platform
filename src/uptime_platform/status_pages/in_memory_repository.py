from uuid import UUID

from uptime_platform.status_pages.entities import (
    StatusPage,
    StatusPageMonitor,
)


class InMemoryStatusPageRepository:
    def __init__(self) -> None:
        self._pages: dict[UUID, StatusPage] = {}
        self._monitors: dict[
            tuple[UUID, UUID],
            StatusPageMonitor,
        ] = {}

    async def create(
        self,
        page: StatusPage,
    ) -> StatusPage:
        self._pages[page.id] = page

        return page

    async def get_by_id(
        self,
        page_id: UUID,
    ) -> StatusPage | None:
        return self._pages.get(page_id)

    async def get_by_slug(
        self,
        slug: str,
    ) -> StatusPage | None:
        for page in self._pages.values():
            if page.slug == slug:
                return page

        return None

    async def get_all(
        self,
    ) -> list[StatusPage]:
        return sorted(
            self._pages.values(),
            key=lambda page: page.created_at,
            reverse=True,
        )

    async def update(
        self,
        page: StatusPage,
    ) -> StatusPage | None:
        if page.id not in self._pages:
            return None

        self._pages[page.id] = page

        return page

    async def delete(
        self,
        page_id: UUID,
    ) -> bool:
        if page_id not in self._pages:
            return False

        del self._pages[page_id]

        self._monitors = {
            key: relation
            for key, relation in self._monitors.items()
            if relation.status_page_id != page_id
        }

        return True

    async def add_monitor(
        self,
        relation: StatusPageMonitor,
    ) -> bool:
        key = (
            relation.status_page_id,
            relation.monitor_id,
        )

        if key in self._monitors:
            return False

        self._monitors[key] = relation

        return True

    async def remove_monitor(
        self,
        page_id: UUID,
        monitor_id: UUID,
    ) -> bool:
        key = (
            page_id,
            monitor_id,
        )

        if key not in self._monitors:
            return False

        del self._monitors[key]

        return True

    async def get_monitors(
        self,
        page_id: UUID,
    ) -> list[StatusPageMonitor]:
        relations = [
            relation
            for relation in self._monitors.values()
            if relation.status_page_id == page_id
        ]

        return sorted(
            relations,
            key=lambda relation: relation.position,
        )
