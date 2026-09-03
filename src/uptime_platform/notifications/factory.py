import httpx2

from uptime_platform.notifications.entities import (
    NotificationDestination,
    NotificationDestinationType,
)
from uptime_platform.notifications.protocols import (
    NotificationChannelProtocol,
)
from uptime_platform.notifications.webhook import (
    WebhookNotificationChannel,
)


def create_notification_channel(
    destination: NotificationDestination,
    http_client: httpx2.AsyncClient,
    webhook_timeout_seconds: float,
) -> NotificationChannelProtocol:
    if destination.destination_type is NotificationDestinationType.WEBHOOK:
        return WebhookNotificationChannel(
            client=http_client,
            url=destination.webhook_url,
            secret=destination.webhook_secret,
            timeout_seconds=webhook_timeout_seconds,
        )

    raise RuntimeError(
        f"Unsupported notification destination type: {destination.destination_type}"
    )
