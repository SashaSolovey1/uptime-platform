import asyncio
import logging

from uptime_platform.core.config import get_settings
from uptime_platform.db.session import SessionFactory
from uptime_platform.notifications.factory import (
    create_notification_channel,
)
from uptime_platform.notifications.worker import (
    NotificationWorker,
)

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s %(levelname)s %(name)s %(message)s"),
    )

    settings = get_settings()

    async with create_notification_channel(settings) as channel:
        logger.info(
            "notification worker started channel=%s",
            settings.notification_channel,
        )

        worker = NotificationWorker(
            session_factory=SessionFactory,
            channel=channel,
        )

        await worker.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
