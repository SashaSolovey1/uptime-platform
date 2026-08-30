from typing import Protocol
from uuid import UUID

from uptime_platform.checks.entities import (
    Check,
    CheckResult,
)


class HttpCheckerProtocol(Protocol):
    async def check(
        self,
        url: str,
        timeout_seconds: int,
    ) -> CheckResult: ...


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
