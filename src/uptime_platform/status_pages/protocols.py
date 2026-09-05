from typing import Protocol
from uuid import UUID

from uptime_platform.status_pages.entities import (
    StatusPage,
    StatusPageMonitor,
)


class StatusPageRepositoryProtocol(Protocol):
    async def create(
        self,
        page: StatusPage,
    ) -> StatusPage: ...

    async def get_by_id(
        self,
        page_id: UUID,
    ) -> StatusPage | None: ...

    async def get_by_slug(
        self,
        slug: str,
    ) -> StatusPage | None: ...

    async def get_all(
        self,
    ) -> list[StatusPage]: ...

    async def update(
        self,
        page: StatusPage,
    ) -> StatusPage | None: ...

    async def delete(
        self,
        page_id: UUID,
    ) -> bool: ...

    async def add_monitor(
        self,
        relation: StatusPageMonitor,
    ) -> bool: ...

    async def remove_monitor(
        self,
        page_id: UUID,
        monitor_id: UUID,
    ) -> bool: ...

    async def get_monitors(
        self,
        page_id: UUID,
    ) -> list[StatusPageMonitor]: ...
