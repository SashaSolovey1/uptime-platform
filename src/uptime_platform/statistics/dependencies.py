from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.db.session import get_db_session
from uptime_platform.monitors.sqlalchemy_repository import (
    SqlAlchemyMonitorRepository,
)
from uptime_platform.statistics.service import (
    StatisticsService,
)
from uptime_platform.statistics.sqlalchemy_repository import (
    SqlAlchemyStatisticsRepository,
)


def get_statistics_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> StatisticsService:
    return StatisticsService(
        repository=SqlAlchemyStatisticsRepository(session),
        monitor_repository=SqlAlchemyMonitorRepository(session),
    )
