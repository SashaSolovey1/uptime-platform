from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from uptime_platform.auth.dependencies import require_admin
from uptime_platform.auth.entities import OrganizationContext
from uptime_platform.status_pages.dependencies import (
    get_public_status_page_service,
    get_status_page_service,
)
from uptime_platform.status_pages.schemas import (
    PublicStatusPageResponse,
    StatusPageCreate,
    StatusPageResponse,
    StatusPageUpdate,
)
from uptime_platform.status_pages.service import (
    PublicStatusPageService,
    StatusPageService,
)

router = APIRouter()


@router.post(
    "/api/v1/status-pages",
    response_model=StatusPageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_status_page(
    data: StatusPageCreate,
    service: Annotated[
        StatusPageService,
        Depends(get_status_page_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> StatusPageResponse:
    page = await service.create(data)

    if page is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Status page slug already exists",
        )

    return StatusPageResponse(
        id=page.id,
        name=page.name,
        slug=page.slug,
        published=page.published,
    )


@router.get(
    "/api/v1/status-pages",
    response_model=list[StatusPageResponse],
)
async def get_status_pages(
    service: Annotated[
        StatusPageService,
        Depends(get_status_page_service),
    ],
) -> list[StatusPageResponse]:
    pages = await service.get_all()

    return [
        StatusPageResponse(
            id=page.id,
            name=page.name,
            slug=page.slug,
            published=page.published,
        )
        for page in pages
    ]


@router.get(
    "/api/v1/status-pages/{page_id}",
    response_model=StatusPageResponse,
)
async def get_status_page(
    page_id: UUID,
    service: Annotated[
        StatusPageService,
        Depends(get_status_page_service),
    ],
) -> StatusPageResponse:
    page = await service.get(page_id)

    if page is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status page not found",
        )

    return StatusPageResponse(
        id=page.id,
        name=page.name,
        slug=page.slug,
        published=page.published,
    )


@router.patch(
    "/api/v1/status-pages/{page_id}",
    response_model=StatusPageResponse,
)
async def update_status_page(
    page_id: UUID,
    data: StatusPageUpdate,
    service: Annotated[
        StatusPageService,
        Depends(get_status_page_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> StatusPageResponse:
    page = await service.update(
        page_id,
        data,
    )

    if page is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status page not found",
        )

    return StatusPageResponse(
        id=page.id,
        name=page.name,
        slug=page.slug,
        published=page.published,
    )


@router.delete(
    "/api/v1/status-pages/{page_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_status_page(
    page_id: UUID,
    service: Annotated[
        StatusPageService,
        Depends(get_status_page_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> Response:
    deleted = await service.delete(page_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status page not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/api/v1/status-pages/{page_id}/monitors/{monitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def add_monitor_to_status_page(
    page_id: UUID,
    monitor_id: UUID,
    service: Annotated[
        StatusPageService,
        Depends(get_status_page_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> Response:
    result = await service.add_monitor(
        page_id,
        monitor_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status page or monitor not found",
        )

    if result is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Monitor already added",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/api/v1/status-pages/{page_id}/monitors/{monitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_monitor_from_status_page(
    page_id: UUID,
    monitor_id: UUID,
    service: Annotated[
        StatusPageService,
        Depends(get_status_page_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> Response:
    removed = await service.remove_monitor(
        page_id,
        monitor_id,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status page monitor not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/status/{slug}",
    response_model=PublicStatusPageResponse,
)
async def get_public_status_page(
    slug: str,
    service: Annotated[
        PublicStatusPageService,
        Depends(get_public_status_page_service),
    ],
) -> PublicStatusPageResponse:
    page = await service.get(slug)

    if page is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status page not found",
        )

    return page
