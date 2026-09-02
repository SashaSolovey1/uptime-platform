from datetime import UTC, datetime
from uuid import uuid4

import pytest

from uptime_platform.notifications.exceptions import NotificationDeliveryError
from uptime_platform.notifications.service import (
    NotificationService,
)
from uptime_platform.outbox.entities import (
    OutboxEvent,
    OutboxEventType,
)

pytestmark = pytest.mark.anyio


class StubNotificationChannel:
    def __init__(self) -> None:
        self.calls = 0

    async def send(
        self,
        event: OutboxEvent,
    ) -> None:
        self.calls += 1


class FailingNotificationChannel:
    def __init__(self) -> None:
        self.calls = 0

    async def send(
        self,
        event: OutboxEvent,
    ) -> None:
        self.calls += 1

        raise NotificationDeliveryError("Notification failed")


def make_event(
    attempts: int = 0,
) -> OutboxEvent:
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
        attempts=attempts,
        last_error=None,
        next_attempt_at=now,
        locked_until=None,
    )


async def test_successful_notification_marks_event_processed() -> None:
    channel = StubNotificationChannel()

    service = NotificationService(channel)

    event = make_event()

    result = await service.process(event)

    assert result.processed_at is not None
    assert result.attempts == 1
    assert result.last_error is None
    assert result.locked_until is None


async def test_failed_notification_schedules_retry() -> None:
    channel = FailingNotificationChannel()

    service = NotificationService(channel)

    event = make_event()

    result = await service.process(event)

    assert result.processed_at is None
    assert result.attempts == 1
    assert result.last_error == "Notification failed"
    assert result.next_attempt_at > event.next_attempt_at
    assert result.locked_until is None


async def test_retry_increments_existing_attempt_count() -> None:
    channel = FailingNotificationChannel()
    service = NotificationService(channel)

    event = make_event(attempts=2)

    result = await service.process(event)

    assert result.processed_at is None
    assert result.attempts == 3
    assert result.last_error == "Notification failed"
