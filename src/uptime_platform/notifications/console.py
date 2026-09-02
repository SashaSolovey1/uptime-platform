import logging

from uptime_platform.outbox.entities import OutboxEvent

logger = logging.getLogger(__name__)


class ConsoleNotificationChannel:
    async def send(
        self,
        event: OutboxEvent,
    ) -> None:
        logger.info(
            "notification event_type=%s incident_id=%s monitor_id=%s",
            event.event_type,
            event.payload.get("incident_id"),
            event.payload.get("monitor_id"),
        )
