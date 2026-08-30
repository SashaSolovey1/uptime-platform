from fastapi import FastAPI

from uptime_platform.checks.router import (
    router as checks_router,
)
from uptime_platform.monitors.router import (
    router as monitors_router,
)

app = FastAPI(
    title="Uptime Platform API",
    version="0.1.0",
)

app.include_router(monitors_router)
app.include_router(checks_router)
