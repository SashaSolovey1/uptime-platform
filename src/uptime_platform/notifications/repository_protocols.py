from typing import Protocol
from uuid import UUID

from uptime_platform.notifications.entities import (
    NotificationDestination,
)


class NotificationDestinationRepositoryProtocol(Protocol):
    async def create(
        self,
        destination: NotificationDestination,
    ) -> NotificationDestination: ...

    async def get_by_id(
        self,
        destination_id: UUID,
    ) -> NotificationDestination | None: ...

    async def get_all(
        self,
    ) -> list[NotificationDestination]: ...

    async def update(
        self,
        destination: NotificationDestination,
    ) -> NotificationDestination | None: ...

    async def delete(
        self,
        destination_id: UUID,
    ) -> bool: ...
