import json
from datetime import UTC, datetime
from uuid import uuid4

import httpx2
import pytest

from uptime_platform.notifications.exceptions import (
    NotificationDeliveryError,
)
from uptime_platform.notifications.telegram import (
    TelegramNotificationChannel,
)
from uptime_platform.organizations.constants import DEFAULT_ORGANIZATION_ID
from uptime_platform.outbox.entities import (
    OutboxEvent,
    OutboxEventType,
)

pytestmark = pytest.mark.anyio


def make_event() -> OutboxEvent:
    return OutboxEvent(
        id=uuid4(),
        organization_id=DEFAULT_ORGANIZATION_ID,
        event_type=OutboxEventType.INCIDENT_OPENED,
        payload={
            "incident_id": str(uuid4()),
            "monitor_id": str(uuid4()),
        },
        created_at=datetime.now(UTC),
        processed_at=None,
    )


async def test_telegram_sends_event() -> None:
    event = make_event()

    captured_request: httpx2.Request | None = None

    def handler(
        request: httpx2.Request,
    ) -> httpx2.Response:
        nonlocal captured_request

        captured_request = request

        return httpx2.Response(
            status_code=200,
            json={
                "ok": True,
            },
        )

    transport = httpx2.MockTransport(handler)

    async with httpx2.AsyncClient(
        transport=transport,
    ) as client:
        channel = TelegramNotificationChannel(
            client=client,
            bot_token="test-token",
            chat_id="123456",
            timeout_seconds=5,
        )

        await channel.send(event)

    assert captured_request is not None
    assert captured_request.method == "POST"

    assert (
        str(captured_request.url)
        == "https://api.telegram.org/bottest-token/sendMessage"
    )

    body = json.loads(captured_request.content)

    assert body["chat_id"] == "123456"
    assert "Incident opened" in body["text"]
    assert event.payload["monitor_id"] in body["text"]
    assert event.payload["incident_id"] in body["text"]


async def test_telegram_http_error_raises_delivery_error() -> None:
    event = make_event()

    def handler(
        request: httpx2.Request,
    ) -> httpx2.Response:
        return httpx2.Response(
            status_code=500,
        )

    transport = httpx2.MockTransport(handler)

    async with httpx2.AsyncClient(
        transport=transport,
    ) as client:
        channel = TelegramNotificationChannel(
            client=client,
            bot_token="test-token",
            chat_id="123456",
            timeout_seconds=5,
        )

        with pytest.raises(NotificationDeliveryError):
            await channel.send(event)
