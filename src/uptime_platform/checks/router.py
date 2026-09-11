from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from uptime_platform.auth.dependencies import require_member
from uptime_platform.auth.entities import OrganizationContext
from uptime_platform.checks.dependencies import (
    get_check_service,
)
from uptime_platform.checks.entities import Check
from uptime_platform.checks.schemas import CheckResponse
from uptime_platform.checks.service import CheckService

router = APIRouter(
    prefix="/api/v1/monitors",
    tags=["checks"],
)


@router.post(
    "/{monitor_id}/checks",
    status_code=status.HTTP_201_CREATED,
    response_model=CheckResponse,
)
async def run_monitor_check(
    monitor_id: UUID,
    service: Annotated[
        CheckService,
        Depends(get_check_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_member),
    ],
) -> Check:
    check = await service.run(monitor_id)

    if check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    return check


@router.get(
    "/{monitor_id}/checks",
    response_model=list[CheckResponse],
)
async def get_monitor_checks(
    monitor_id: UUID,
    service: Annotated[
        CheckService,
        Depends(get_check_service),
    ],
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=500,
        ),
    ] = 50,
) -> list[Check]:
    checks = await service.get_history(
        monitor_id=monitor_id,
        limit=limit,
    )

    if checks is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    return checks
