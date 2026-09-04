from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.db.session import get_db_session
from uptime_platform.maintenance.protocols import (
    MaintenanceWindowRepositoryProtocol,
)
from uptime_platform.maintenance.service import (
    MaintenanceWindowService,
)
from uptime_platform.maintenance.sqlalchemy_repository import (
    SqlAlchemyMaintenanceWindowRepository,
)
from uptime_platform.monitors.protocols import (
    MonitorRepositoryProtocol,
)
from uptime_platform.monitors.sqlalchemy_repository import (
    SqlAlchemyMonitorRepository,
)


def get_maintenance_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> MaintenanceWindowRepositoryProtocol:
    return SqlAlchemyMaintenanceWindowRepository(session)


def get_maintenance_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> MaintenanceWindowService:
    maintenance_repository = SqlAlchemyMaintenanceWindowRepository(session)

    monitor_repository: MonitorRepositoryProtocol = SqlAlchemyMonitorRepository(session)

    return MaintenanceWindowService(
        repository=maintenance_repository,
        monitor_repository=monitor_repository,
    )
