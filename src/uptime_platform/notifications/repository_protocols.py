from datetime import datetime
from typing import Protocol
from uuid import UUID

from uptime_platform.notifications.entities import (
    NotificationDelivery,
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

    async def get_enabled(
        self,
    ) -> list[NotificationDestination]: ...


class NotificationDeliveryRepositoryProtocol(Protocol):
    async def create(
        self,
        delivery: NotificationDelivery,
    ) -> NotificationDelivery: ...

    async def get_by_id(
        self,
        delivery_id: UUID,
    ) -> NotificationDelivery | None: ...

    async def claim_pending(
        self,
        limit: int,
        max_attempts: int,
        now: datetime,
        locked_until: datetime,
    ) -> list[NotificationDelivery]: ...

    async def update(
        self,
        delivery: NotificationDelivery,
    ) -> NotificationDelivery | None: ...

    async def create_if_missing(
        self,
        delivery: NotificationDelivery,
    ) -> bool: ...

    async def release_lock(
        self,
        delivery_id: UUID,
    ) -> None: ...
