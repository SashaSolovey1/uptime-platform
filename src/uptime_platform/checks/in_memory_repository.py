from datetime import UTC, datetime
from uuid import UUID

from uptime_platform.checks.entities import Check, CheckResult


class InMemoryCheckRepository:
    def __init__(self) -> None:
        self._checks: list[Check] = []

    async def create(
        self,
        monitor_id: UUID,
        result: CheckResult,
    ) -> Check:
        check = Check(
            id=len(self._checks) + 1,
            monitor_id=monitor_id,
            success=result.success,
            response_time_ms=result.response_time_ms,
            status_code=result.status_code,
            error=result.error,
            checked_at=datetime.now(UTC),
        )

        self._checks.append(check)

        return check

    async def get_by_monitor_id(
        self,
        monitor_id: UUID,
        limit: int,
    ) -> list[Check]:
        checks = [check for check in self._checks if check.monitor_id == monitor_id]

        return list(reversed(checks[-limit:]))
