from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.db.session import get_db_session
from uptime_platform.monitors.sqlalchemy_repository import (
    SqlAlchemyMonitorRepository,
)
from uptime_platform.status_pages.service import (
    StatusPageService,
)
from uptime_platform.status_pages.sqlalchemy_repository import (
    SqlAlchemyStatusPageRepository,
)


def get_status_page_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> StatusPageService:
    return StatusPageService(
        repository=SqlAlchemyStatusPageRepository(session),
        monitor_repository=SqlAlchemyMonitorRepository(session),
    )
