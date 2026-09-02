from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.db.session import get_db_session
from uptime_platform.incidents.protocols import (
    IncidentRepositoryProtocol,
)
from uptime_platform.incidents.service import (
    IncidentService,
)
from uptime_platform.incidents.sqlalchemy_repository import (
    SqlAlchemyIncidentRepository,
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
) -> IncidentService:
    return IncidentService(repository)
