import time

import httpx2

from uptime_platform.checks.entities import CheckResult


class HttpChecker:
    async def check(self, url: str, timeout_seconds: int) -> CheckResult:
        started_at = time.perf_counter()

        try:
            async with httpx2.AsyncClient() as client:
                response = await client.get(url, timeout=timeout_seconds)

            response_time_ms = (time.perf_counter() - started_at) * 1000

            return CheckResult(
                success=response.is_success,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                error=None,
            )

        except httpx2.HTTPError as exc:
            response_time_ms = (time.perf_counter() - started_at) * 1000

            return CheckResult(
                success=False,
                response_time_ms=response_time_ms,
                status_code=None,
                error=str(exc),
            )
