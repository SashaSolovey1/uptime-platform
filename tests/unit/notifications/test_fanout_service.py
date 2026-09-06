from datetime import UTC, datetime
from uuid import uuid4

import pytest

from uptime_platform.notifications.entities import (
    NotificationDestination,
    NotificationDestinationType,
    WebhookDestinationConfig,
)
from uptime_platform.notifications.in_memory_repository import (
    InMemoryNotificationDeliveryRepository,
    InMemoryNotificationDestinationRepository,
)
from uptime_platform.notifications.service import (
    NotificationFanoutService,
)
from uptime_platform.outbox.entities import (
    OutboxEvent,
    OutboxEventType,
)
from uptime_platform.outbox.in_memory_repository import (
    InMemoryOutboxRepository,
)

pytestmark = pytest.mark.anyio


def make_destination(
    *,
    enabled: bool = True,
) -> NotificationDestination:
    return NotificationDestination(
        id=uuid4(),
        name="Test webhook",
        destination_type=NotificationDestinationType.WEBHOOK,
        enabled=enabled,
        config=WebhookDestinationConfig(
            url="https://example.com/webhook",
            secret="test-secret",
        ),
        created_at=datetime.now(UTC),
    )


def make_event() -> OutboxEvent:
    now = datetime.now(UTC)

    return OutboxEvent(
        id=uuid4(),
        event_type=OutboxEventType.INCIDENT_OPENED,
        payload={
            "incident_id": str(uuid4()),
            "monitor_id": str(uuid4()),
        },
        created_at=now,
        processed_at=None,
    )


async def test_fan_out_creates_delivery_for_each_enabled_destination() -> None:
    destination_repository = InMemoryNotificationDestinationRepository()

    delivery_repository = InMemoryNotificationDeliveryRepository()

    outbox_repository = InMemoryOutboxRepository()

    destination_1 = make_destination()
    destination_2 = make_destination()

    await destination_repository.create(destination_1)

    await destination_repository.create(destination_2)

    event = make_event()

    await outbox_repository.create(event)

    service = NotificationFanoutService(
        destination_repository=destination_repository,
        delivery_repository=delivery_repository,
        outbox_repository=outbox_repository,
    )

    deliveries = await service.fan_out(event)

    assert len(deliveries) == 2

    assert {delivery.destination_id for delivery in deliveries} == {
        destination_1.id,
        destination_2.id,
    }

    assert all(delivery.event_id == event.id for delivery in deliveries)

    processed_event = await outbox_repository.get_by_id(event.id)

    assert processed_event is not None
    assert processed_event.processed_at is not None


async def test_fan_out_skips_disabled_destinations() -> None:
    destination_repository = InMemoryNotificationDestinationRepository()

    delivery_repository = InMemoryNotificationDeliveryRepository()

    outbox_repository = InMemoryOutboxRepository()

    enabled_destination = make_destination(enabled=True)

    disabled_destination = make_destination(enabled=False)

    await destination_repository.create(enabled_destination)

    await destination_repository.create(disabled_destination)

    event = make_event()

    await outbox_repository.create(event)

    service = NotificationFanoutService(
        destination_repository=destination_repository,
        delivery_repository=delivery_repository,
        outbox_repository=outbox_repository,
    )

    deliveries = await service.fan_out(event)

    assert len(deliveries) == 1

    assert deliveries[0].destination_id == enabled_destination.id


async def test_fan_out_does_not_create_duplicate_deliveries() -> None:
    destination_repository = InMemoryNotificationDestinationRepository()

    delivery_repository = InMemoryNotificationDeliveryRepository()

    outbox_repository = InMemoryOutboxRepository()

    destination = make_destination()

    await destination_repository.create(destination)

    event = make_event()

    await outbox_repository.create(event)

    service = NotificationFanoutService(
        destination_repository=destination_repository,
        delivery_repository=delivery_repository,
        outbox_repository=outbox_repository,
    )

    first_result = await service.fan_out(event)

    second_result = await service.fan_out(event)

    assert len(first_result) == 1
    assert len(second_result) == 0


async def test_fan_out_marks_event_processed_when_no_destinations_exist() -> None:
    destination_repository = InMemoryNotificationDestinationRepository()

    delivery_repository = InMemoryNotificationDeliveryRepository()

    outbox_repository = InMemoryOutboxRepository()

    event = make_event()

    await outbox_repository.create(event)

    service = NotificationFanoutService(
        destination_repository=destination_repository,
        delivery_repository=delivery_repository,
        outbox_repository=outbox_repository,
    )

    deliveries = await service.fan_out(event)

    assert deliveries == []

    processed_event = await outbox_repository.get_by_id(event.id)

    assert processed_event is not None
    assert processed_event.processed_at is not None
