from uuid import UUID

from uptime_platform.checks.entities import Check
from uptime_platform.checks.protocols import (
    CheckRepositoryProtocol,
    HttpCheckerProtocol,
)
from uptime_platform.monitors.protocols import (
    MonitorRepositoryProtocol,
)


class CheckService:
    def __init__(
        self,
        monitor_repository: MonitorRepositoryProtocol,
        check_repository: CheckRepositoryProtocol,
        checker: HttpCheckerProtocol,
    ) -> None:
        self._monitor_repository = monitor_repository
        self._check_repository = check_repository
        self._checker = checker

    async def run(self, monitor_id: UUID) -> Check | None:
        monitor = await self._monitor_repository.get_by_id(monitor_id)

        if monitor is None:
            return None

        result = await self._checker.check(
            url=monitor.url, timeout_seconds=monitor.timeout_seconds
        )

        return await self._check_repository.create(
            monitor_id=monitor.id,
            result=result,
        )

    async def get_history(self, monitor_id: UUID, limit: int) -> list[Check] | None:
        monitor = await self._monitor_repository.get_by_id(monitor_id)

        if monitor is None:
            return None

        return await self._check_repository.get_by_monitor_id(
            monitor_id=monitor_id,
            limit=limit,
        )
