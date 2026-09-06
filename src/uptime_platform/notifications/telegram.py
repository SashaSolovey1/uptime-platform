import httpx2

from uptime_platform.notifications.exceptions import (
    NotificationDeliveryError,
)
from uptime_platform.outbox.entities import (
    OutboxEvent,
    OutboxEventType,
)


class TelegramNotificationChannel:
    def __init__(
        self,
        client: httpx2.AsyncClient,
        bot_token: str,
        chat_id: str,
        timeout_seconds: int,
    ) -> None:
        self._client = client
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._timeout_seconds = timeout_seconds

    async def send(
        self,
        event: OutboxEvent,
    ) -> None:
        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"

        try:
            response = await self._client.post(
                url,
                json={
                    "chat_id": self._chat_id,
                    "text": self._format_event(event),
                },
                timeout=self._timeout_seconds,
            )
        except httpx2.RequestError as exc:
            raise NotificationDeliveryError("Telegram request failed") from exc

        if response.is_error:
            raise NotificationDeliveryError(
                f"Telegram API returned HTTP {response.status_code}"
            )

    @staticmethod
    def _format_event(
        event: OutboxEvent,
    ) -> str:
        incident_id = event.payload.get(
            "incident_id",
            "unknown",
        )
        monitor_id = event.payload.get(
            "monitor_id",
            "unknown",
        )

        if event.event_type is OutboxEventType.INCIDENT_OPENED:
            title = "Incident opened"

        elif event.event_type is OutboxEventType.INCIDENT_RESOLVED:
            title = "Incident resolved"

        else:
            title = str(event.event_type)

        return f"{title}\nMonitor ID: {monitor_id}\nIncident ID: {incident_id}"
