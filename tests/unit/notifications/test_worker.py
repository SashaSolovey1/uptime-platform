from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from uptime_platform.notifications.entities import (
    NotificationDelivery,
)
from uptime_platform.notifications.worker import (
    NotificationWorker,
)

pytestmark = pytest.mark.anyio


def make_delivery() -> NotificationDelivery:
    now = datetime.now(UTC)

    return NotificationDelivery(
        id=uuid4(),
        event_id=uuid4(),
        destination_id=uuid4(),
        created_at=now,
        processed_at=None,
        attempts=0,
        last_error=None,
        next_attempt_at=now,
        locked_until=now,
    )


async def test_unexpected_error_releases_delivery_lock() -> None:
    delivery = make_delivery()

    worker = NotificationWorker(
        session_factory=MagicMock(),
        http_client=MagicMock(),
    )

    process_delivery = AsyncMock(side_effect=RuntimeError("boom"))
    release_delivery_lock = AsyncMock()

    worker._process_delivery = process_delivery
    worker._release_delivery_lock = release_delivery_lock

    await worker._process_delivery_safely(delivery)

    process_delivery.assert_awaited_once_with(delivery)

    release_delivery_lock.assert_awaited_once_with(delivery)


async def test_successful_processing_does_not_release_lock() -> None:
    delivery = make_delivery()

    worker = NotificationWorker(
        session_factory=MagicMock(),
        http_client=MagicMock(),
    )

    process_delivery = AsyncMock()
    release_delivery_lock = AsyncMock()

    worker._process_delivery = process_delivery
    worker._release_delivery_lock = release_delivery_lock

    await worker._process_delivery_safely(delivery)

    process_delivery.assert_awaited_once_with(delivery)

    release_delivery_lock.assert_not_awaited()
