from fastapi import FastAPI

from uptime_platform.checks.router import (
    router as checks_router,
)
from uptime_platform.incidents.router import (
    router as incidents_router,
)
from uptime_platform.maintenance.router import (
    router as maintenance_router,
)
from uptime_platform.monitors.router import (
    router as monitors_router,
)
from uptime_platform.notifications.router import (
    router as notifications_router,
)

app = FastAPI(
    title="Uptime Platform API",
    version="0.1.0",
)


@app.get(
    "/health",
    include_in_schema=False,
)
async def health() -> dict[str, str]:
    return {
        "status": "ok",
    }


app.include_router(monitors_router)
app.include_router(checks_router)
app.include_router(incidents_router)
app.include_router(notifications_router)
app.include_router(maintenance_router)
