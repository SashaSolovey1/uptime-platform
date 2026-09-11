from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.auth.dependencies import (
    get_organization_context,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.db.session import get_db_session
from uptime_platform.incidents.protocols import (
    IncidentRepositoryProtocol,
)
from uptime_platform.incidents.service import IncidentService
from uptime_platform.incidents.sqlalchemy_repository import (
    SqlAlchemyIncidentRepository,
)
from uptime_platform.monitors.dependencies import (
    get_monitor_repository,
)
from uptime_platform.monitors.protocols import (
    MonitorRepositoryProtocol,
)


def get_incident_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> IncidentRepositoryProtocol:
    return SqlAlchemyIncidentRepository(session)


def get_incident_service(
    repository: Annotated[
        IncidentRepositoryProtocol,
        Depends(get_incident_repository),
    ],
    monitor_repository: Annotated[
        MonitorRepositoryProtocol,
        Depends(get_monitor_repository),
    ],
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
) -> IncidentService:
    return IncidentService(
        repository=repository,
        monitor_repository=monitor_repository,
        organization_id=context.organization.id,
    )
