import asyncio
import logging

from uptime_platform.db.session import (
    SessionFactory,
)
from uptime_platform.scheduler.scheduler import (
    Scheduler,
)

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    logger.info("scheduler started")

    scheduler = Scheduler(
        session_factory=SessionFactory,
    )

    await scheduler.run_forever()


def run() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("scheduler stopped")


if __name__ == "__main__":
    run()
