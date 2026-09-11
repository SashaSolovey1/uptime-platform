from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from uptime_platform.auth.dependencies import (
    require_member,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.monitors.dependencies import get_monitor_service
from uptime_platform.monitors.entities import Monitor
from uptime_platform.monitors.exceptions import InvalidMonitorConfigError
from uptime_platform.monitors.schemas import (
    MonitorCreate,
    MonitorResponse,
    MonitorUpdate,
)
from uptime_platform.monitors.service import MonitorService

router = APIRouter(
    prefix="/api/v1/monitors",
    tags=["monitors"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=MonitorResponse,
)
async def create_monitor(
    monitor: MonitorCreate,
    service: Annotated[
        MonitorService,
        Depends(get_monitor_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_member),
    ],
) -> Monitor:
    return await service.create(monitor)


@router.get(
    "",
    response_model=list[MonitorResponse],
)
async def list_monitors(
    service: Annotated[
        MonitorService,
        Depends(get_monitor_service),
    ],
) -> list[Monitor]:
    return await service.get_all()


@router.get(
    "/{monitor_id}",
    response_model=MonitorResponse,
)
async def get_monitor(
    monitor_id: UUID,
    service: Annotated[
        MonitorService,
        Depends(get_monitor_service),
    ],
) -> Monitor:
    monitor = await service.get_by_id(monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    return monitor


@router.patch(
    "/{monitor_id}",
    response_model=MonitorResponse,
)
async def update_monitor(
    monitor_id: UUID,
    data: MonitorUpdate,
    service: Annotated[
        MonitorService,
        Depends(get_monitor_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_member),
    ],
) -> Monitor:
    try:
        monitor = await service.update(
            monitor_id,
            data,
        )
    except InvalidMonitorConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    return monitor


@router.delete(
    "/{monitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_monitor(
    monitor_id: UUID,
    service: Annotated[
        MonitorService,
        Depends(get_monitor_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_member),
    ],
) -> None:
    deleted = await service.delete(monitor_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )
