from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from uptime_platform.incidents.dependencies import (
    get_incident_service,
)
from uptime_platform.incidents.entities import (
    Incident,
    IncidentStatus,
)
from uptime_platform.incidents.schemas import (
    IncidentResponse,
)
from uptime_platform.incidents.service import (
    IncidentService,
)

router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["incidents"],
)


@router.get(
    "",
    response_model=list[IncidentResponse],
)
async def list_incidents(
    service: Annotated[
        IncidentService,
        Depends(get_incident_service),
    ],
    status_filter: Annotated[
        IncidentStatus | None,
        Query(alias="status"),
    ] = None,
    monitor_id: UUID | None = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=500,
        ),
    ] = 100,
) -> list[Incident]:
    return await service.get_all(
        status=status_filter,
        monitor_id=monitor_id,
        limit=limit,
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def get_incident(
    incident_id: UUID,
    service: Annotated[
        IncidentService,
        Depends(get_incident_service),
    ],
) -> Incident:
    incident = await service.get_by_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident
