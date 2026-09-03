import asyncio
import logging

import httpx2

from uptime_platform.core.config import (
    get_settings,
)
from uptime_platform.db.session import (
    SessionFactory,
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

    logger.info("notification worker started")

    async with httpx2.AsyncClient() as client:
        worker = NotificationWorker(
            session_factory=SessionFactory,
            http_client=client,
            webhook_timeout_seconds=(settings.webhook_timeout_seconds),
        )

        await worker.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
