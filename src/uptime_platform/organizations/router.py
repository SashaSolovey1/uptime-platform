from typing import Annotated

from fastapi import APIRouter, Depends, status

from uptime_platform.auth.dependencies import (
    get_current_user,
)
from uptime_platform.organizations.dependencies import (
    get_organization_service,
)
from uptime_platform.organizations.entities import (
    OrganizationAccess,
)
from uptime_platform.organizations.schemas import (
    OrganizationCreate,
    OrganizationResponse,
)
from uptime_platform.organizations.service import (
    OrganizationService,
)
from uptime_platform.users.entities import User

router = APIRouter(
    prefix="/api/v1/organizations",
    tags=["organizations"],
)


def _to_response(
    access: OrganizationAccess,
) -> OrganizationResponse:
    return OrganizationResponse(
        id=access.organization.id,
        name=access.organization.name,
        role=access.membership.role,
        created_at=access.organization.created_at,
    )


@router.get(
    "",
    response_model=list[OrganizationResponse],
)
async def get_organizations(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        OrganizationService,
        Depends(get_organization_service),
    ],
) -> list[OrganizationResponse]:
    accesses = await service.get_for_user(current_user.id)

    return [_to_response(access) for access in accesses]


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    data: OrganizationCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        OrganizationService,
        Depends(get_organization_service),
    ],
) -> OrganizationResponse:
    access = await service.create(
        user_id=current_user.id,
        data=data,
    )

    return _to_response(access)
