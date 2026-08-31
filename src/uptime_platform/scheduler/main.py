import asyncio

from uptime_platform.db.session import (
    SessionFactory,
)
from uptime_platform.scheduler.scheduler import (
    Scheduler,
)


async def main() -> None:
    scheduler = Scheduler(
        session_factory=SessionFactory,
    )

    await scheduler.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
