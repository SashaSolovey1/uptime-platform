from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx2

from uptime_platform.core.config import Settings
from uptime_platform.notifications.console import (
    ConsoleNotificationChannel,
)
from uptime_platform.notifications.protocols import (
    NotificationChannelProtocol,
)
from uptime_platform.notifications.webhook import (
    WebhookNotificationChannel,
)


@asynccontextmanager
async def create_notification_channel(
    settings: Settings,
) -> AsyncIterator[NotificationChannelProtocol]:
    if settings.notification_channel == "console":
        yield ConsoleNotificationChannel()
        return
    if settings.notification_channel == "webhook":
        if settings.webhook_url is None:
            raise RuntimeError(
                "WEBHOOK_URL is required when NOTIFICATION_CHANNEL=webhook"
            )

        if settings.webhook_secret is None:
            raise RuntimeError(
                "WEBHOOK_SECRET is required when NOTIFICATION_CHANNEL=webhook"
            )

        async with httpx2.AsyncClient() as client:
            yield WebhookNotificationChannel(
                client=client,
                url=settings.webhook_url,
                secret=settings.webhook_secret.get_secret_value(),
                timeout_seconds=settings.webhook_timeout_seconds,
            )

        return

    raise RuntimeError(
        f"Unsupported notification channel: {settings.notification_channel}"
    )
