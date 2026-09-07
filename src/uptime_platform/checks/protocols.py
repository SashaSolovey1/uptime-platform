from typing import Protocol
from uuid import UUID

from uptime_platform.checks.entities import (
    Check,
    CheckResult,
)
from uptime_platform.monitors.entities import Monitor


class CheckerProtocol(Protocol):
    async def check(
        self,
        timeout_seconds: int,
    ) -> CheckResult: ...


class CheckerFactoryProtocol(Protocol):
    def create(
        self,
        monitor: Monitor,
    ) -> CheckerProtocol: ...


class CheckRepositoryProtocol(Protocol):
    async def create(
        self,
        monitor_id: UUID,
        result: CheckResult,
    ) -> Check: ...

    async def get_by_monitor_id(
        self,
        monitor_id: UUID,
        limit: int,
    ) -> list[Check]: ...
