from dataclasses import replace
from datetime import timedelta
from uuid import UUID

from uptime_platform.checks.entities import Check, CheckResult
from uptime_platform.checks.protocols import (
    CheckRepositoryProtocol,
    HttpCheckerProtocol,
)
from uptime_platform.monitors.protocols import (
    MonitorRepositoryProtocol,
)
from uptime_platform.monitors.state import (
    apply_check_result,
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

    async def run(
        self,
        monitor_id: UUID,
    ) -> Check | None:
        monitor = await self._monitor_repository.get_by_id(monitor_id)

        if monitor is None:
            return None

        result = await self._checker.check(
            url=monitor.url,
            timeout_seconds=monitor.timeout_seconds,
        )

        return await self.record(
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

    async def record(
        self,
        monitor_id: UUID,
        result: CheckResult,
    ) -> Check | None:
        monitor = await self._monitor_repository.get_by_id(monitor_id)

        if monitor is None:
            return None

        check = await self._check_repository.create(
            monitor_id=monitor.id,
            result=result,
        )

        updated_monitor = apply_check_result(
            monitor=monitor,
            success=result.success,
        )

        updated_monitor = replace(
            updated_monitor,
            next_check_at=(
                check.checked_at + timedelta(seconds=monitor.interval_seconds)
            ),
        )

        await self._monitor_repository.update(updated_monitor)

        return check
