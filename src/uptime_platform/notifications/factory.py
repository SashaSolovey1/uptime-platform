import httpx2

from uptime_platform.notifications.entities import (
    NotificationDestination,
    NotificationDestinationType,
    TelegramDestinationConfig,
    WebhookDestinationConfig,
)
from uptime_platform.notifications.protocols import (
    NotificationChannelProtocol,
)
from uptime_platform.notifications.telegram import (
    TelegramNotificationChannel,
)
from uptime_platform.notifications.webhook import (
    WebhookNotificationChannel,
)


def create_notification_channel(
    destination: NotificationDestination,
    client: httpx2.AsyncClient,
    timeout_seconds: int,
) -> NotificationChannelProtocol:
    if destination.destination_type is NotificationDestinationType.WEBHOOK:
        if not isinstance(
            destination.config,
            WebhookDestinationConfig,
        ):
            raise TypeError("Webhook destination has invalid config")

        return WebhookNotificationChannel(
            client=client,
            url=destination.config.url,
            secret=destination.config.secret,
            timeout_seconds=timeout_seconds,
        )

    if destination.destination_type is NotificationDestinationType.TELEGRAM:
        if not isinstance(
            destination.config,
            TelegramDestinationConfig,
        ):
            raise TypeError("Telegram destination has invalid config")

        return TelegramNotificationChannel(
            client=client,
            bot_token=destination.config.bot_token,
            chat_id=destination.config.chat_id,
            timeout_seconds=timeout_seconds,
        )

    raise ValueError(
        f"Unsupported notification destination type: {destination.destination_type}"
    )
