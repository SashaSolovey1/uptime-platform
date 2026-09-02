import asyncio
import logging

from uptime_platform.db.session import SessionFactory
from uptime_platform.notifications.console import (
    ConsoleNotificationChannel,
)
from uptime_platform.notifications.worker import (
    NotificationWorker,
)


logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
    )

    logger.info(
        "notification worker started"
    )

    channel = ConsoleNotificationChannel()

    worker = NotificationWorker(
        session_factory=SessionFactory,
        channel=channel,
    )

    await worker.run_forever()


if __name__ == "__main__":
    asyncio.run(main())