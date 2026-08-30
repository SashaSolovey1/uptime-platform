from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.db.session import get_db_session
from uptime_platform.monitors.protocols import MonitorRepositoryProtocol
from uptime_platform.monitors.service import MonitorService
from uptime_platform.monitors.sqlalchemy_repository import (
    SqlAlchemyMonitorRepository,
)


def get_monitor_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> MonitorRepositoryProtocol:
    return SqlAlchemyMonitorRepository(session)


def get_monitor_service(
    repository: Annotated[
        MonitorRepositoryProtocol,
        Depends(get_monitor_repository),
    ],
) -> MonitorService:
    return MonitorService(repository)
