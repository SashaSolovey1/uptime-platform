from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.auth.dependencies import (
    get_organization_context,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.checks.factory import (
    CheckerFactory,
)
from uptime_platform.checks.protocols import (
    CheckerFactoryProtocol,
    CheckRepositoryProtocol,
)
from uptime_platform.checks.service import CheckService
from uptime_platform.checks.sqlalchemy_repository import (
    SqlAlchemyCheckRepository,
)
from uptime_platform.db.session import get_db_session
from uptime_platform.incidents.dependencies import (
    get_incident_repository,
)
from uptime_platform.incidents.protocols import (
    IncidentRepositoryProtocol,
)
from uptime_platform.maintenance.dependencies import (
    get_maintenance_repository,
)
from uptime_platform.maintenance.protocols import (
    MaintenanceWindowRepositoryProtocol,
)
from uptime_platform.monitors.dependencies import get_monitor_repository
from uptime_platform.monitors.protocols import MonitorRepositoryProtocol
from uptime_platform.outbox.dependencies import (
    get_outbox_repository,
)
from uptime_platform.outbox.protocols import (
    OutboxRepositoryProtocol,
)


def get_checker_factory() -> CheckerFactoryProtocol:
    return CheckerFactory()


def get_check_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> CheckRepositoryProtocol:
    return SqlAlchemyCheckRepository(session)


def get_check_service(
    monitor_repository: Annotated[
        MonitorRepositoryProtocol,
        Depends(get_monitor_repository),
    ],
    check_repository: Annotated[
        CheckRepositoryProtocol,
        Depends(get_check_repository),
    ],
    incident_repository: Annotated[
        IncidentRepositoryProtocol,
        Depends(get_incident_repository),
    ],
    outbox_repository: Annotated[
        OutboxRepositoryProtocol,
        Depends(get_outbox_repository),
    ],
    maintenance_repository: Annotated[
        MaintenanceWindowRepositoryProtocol,
        Depends(get_maintenance_repository),
    ],
    checker_factory: Annotated[
        CheckerFactoryProtocol,
        Depends(get_checker_factory),
    ],
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
) -> CheckService:
    return CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        incident_repository=incident_repository,
        outbox_repository=outbox_repository,
        maintenance_repository=maintenance_repository,
        checker_factory=checker_factory,
        organization_id=context.organization.id,
    )
