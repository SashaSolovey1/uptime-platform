from datetime import UTC, datetime
from uuid import uuid4

import httpx2

from uptime_platform.notifications.entities import (
    NotificationDestination,
    NotificationDestinationType,
    TelegramDestinationConfig,
    WebhookDestinationConfig,
)
from uptime_platform.notifications.factory import (
    create_notification_channel,
)
from uptime_platform.notifications.telegram import (
    TelegramNotificationChannel,
)
from uptime_platform.notifications.webhook import (
    WebhookNotificationChannel,
)


def test_factory_creates_webhook_channel() -> None:
    destination = NotificationDestination(
        id=uuid4(),
        name="Webhook",
        destination_type=(NotificationDestinationType.WEBHOOK),
        enabled=True,
        config=WebhookDestinationConfig(
            url="https://example.com/webhook",
            secret="secret",
        ),
        created_at=datetime.now(UTC),
    )

    client = httpx2.AsyncClient()

    channel = create_notification_channel(
        destination=destination,
        client=client,
        timeout_seconds=5,
    )

    assert isinstance(
        channel,
        WebhookNotificationChannel,
    )


def test_factory_creates_telegram_channel() -> None:
    destination = NotificationDestination(
        id=uuid4(),
        name="Telegram",
        destination_type=(NotificationDestinationType.TELEGRAM),
        enabled=True,
        config=TelegramDestinationConfig(
            bot_token="test-token",
            chat_id="123456",
        ),
        created_at=datetime.now(UTC),
    )

    client = httpx2.AsyncClient()

    channel = create_notification_channel(
        destination=destination,
        client=client,
        timeout_seconds=5,
    )

    assert isinstance(
        channel,
        TelegramNotificationChannel,
    )
