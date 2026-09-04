from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from uptime_platform.maintenance.dependencies import (
    get_maintenance_service,
)
from uptime_platform.maintenance.schemas import (
    MaintenanceWindowCreate,
    MaintenanceWindowResponse,
)
from uptime_platform.maintenance.service import (
    MaintenanceWindowService,
)

router = APIRouter(
    prefix="/api/v1/maintenance-windows",
    tags=["maintenance"],
)


@router.post(
    "",
    response_model=MaintenanceWindowResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_maintenance_window(
    data: MaintenanceWindowCreate,
    service: Annotated[
        MaintenanceWindowService,
        Depends(get_maintenance_service),
    ],
) -> MaintenanceWindowResponse:
    window = await service.create(data)

    if window is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )

    return MaintenanceWindowResponse.model_validate(window)


@router.get(
    "",
    response_model=list[MaintenanceWindowResponse],
)
async def get_maintenance_windows(
    service: Annotated[
        MaintenanceWindowService,
        Depends(get_maintenance_service),
    ],
    monitor_id: Annotated[
        UUID | None,
        Query(),
    ] = None,
) -> list[MaintenanceWindowResponse]:
    windows = await service.get_all(monitor_id=monitor_id)

    return [MaintenanceWindowResponse.model_validate(window) for window in windows]


@router.get(
    "/{window_id}",
    response_model=MaintenanceWindowResponse,
)
async def get_maintenance_window(
    window_id: UUID,
    service: Annotated[
        MaintenanceWindowService,
        Depends(get_maintenance_service),
    ],
) -> MaintenanceWindowResponse:
    window = await service.get(window_id)

    if window is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance window not found",
        )

    return MaintenanceWindowResponse.model_validate(window)


@router.delete(
    "/{window_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_maintenance_window(
    window_id: UUID,
    service: Annotated[
        MaintenanceWindowService,
        Depends(get_maintenance_service),
    ],
) -> Response:
    deleted = await service.delete(window_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance window not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
