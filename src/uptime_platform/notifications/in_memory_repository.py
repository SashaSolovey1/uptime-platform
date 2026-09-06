from dataclasses import replace
from datetime import datetime
from uuid import UUID

from uptime_platform.notifications.entities import (
    NotificationDelivery,
    NotificationDestination,
)


class InMemoryNotificationDestinationRepository:
    def __init__(self) -> None:
        self._destinations: dict[
            UUID,
            NotificationDestination,
        ] = {}

    async def create(
        self,
        destination: NotificationDestination,
    ) -> NotificationDestination:
        self._destinations[destination.id] = destination

        return destination

    async def get_by_id(
        self,
        destination_id: UUID,
    ) -> NotificationDestination | None:
        return self._destinations.get(destination_id)

    async def get_all(
        self,
    ) -> list[NotificationDestination]:
        return list(self._destinations.values())

    async def update(
        self,
        destination: NotificationDestination,
    ) -> NotificationDestination | None:
        if destination.id not in self._destinations:
            return None

        self._destinations[destination.id] = destination

        return destination

    async def delete(
        self,
        destination_id: UUID,
    ) -> bool:
        if destination_id not in self._destinations:
            return False

        del self._destinations[destination_id]

        return True

    async def get_enabled(
        self,
    ) -> list[NotificationDestination]:
        return [
            destination
            for destination in self._destinations.values()
            if destination.enabled
        ]


class InMemoryNotificationDeliveryRepository:
    def __init__(self) -> None:
        self._deliveries: dict[
            UUID,
            NotificationDelivery,
        ] = {}

    async def create(
        self,
        delivery: NotificationDelivery,
    ) -> NotificationDelivery:
        self._deliveries[delivery.id] = delivery

        return delivery

    async def get_by_id(
        self,
        delivery_id: UUID,
    ) -> NotificationDelivery | None:
        return self._deliveries.get(delivery_id)

    async def claim_pending(
        self,
        limit: int,
        max_attempts: int,
        now: datetime,
        locked_until: datetime,
    ) -> list[NotificationDelivery]:
        deliveries = [
            delivery
            for delivery in self._deliveries.values()
            if (
                delivery.processed_at is None
                and delivery.attempts < max_attempts
                and delivery.next_attempt_at <= now
                and (delivery.locked_until is None or delivery.locked_until <= now)
            )
        ]

        deliveries.sort(key=lambda delivery: delivery.next_attempt_at)

        deliveries = deliveries[:limit]

        claimed = []

        for delivery in deliveries:
            claimed_delivery = replace(
                delivery,
                locked_until=locked_until,
            )

            self._deliveries[delivery.id] = claimed_delivery

            claimed.append(claimed_delivery)

        return claimed

    async def update(
        self,
        delivery: NotificationDelivery,
    ) -> NotificationDelivery | None:
        if delivery.id not in self._deliveries:
            return None

        self._deliveries[delivery.id] = delivery

        return delivery

    async def create_if_missing(
        self,
        delivery: NotificationDelivery,
    ) -> bool:
        already_exists = any(
            existing.event_id == delivery.event_id
            and existing.destination_id == delivery.destination_id
            for existing in self._deliveries.values()
        )

        if already_exists:
            return False

        self._deliveries[delivery.id] = delivery

        return True

    async def release_lock(
        self,
        delivery_id: UUID,
    ) -> None:
        delivery = self._deliveries.get(delivery_id)

        if delivery is None:
            return

        self._deliveries[delivery_id] = replace(
            delivery,
            locked_until=None,
        )
