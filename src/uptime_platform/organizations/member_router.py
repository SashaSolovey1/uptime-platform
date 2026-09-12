from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from uptime_platform.auth.dependencies import (
    require_admin,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.organizations.exceptions import (
    LastOrganizationOwnerError,
    OrganizationMemberAlreadyExistsError,
    OrganizationMemberNotFoundError,
    OrganizationMemberPermissionError,
    OrganizationUserNotFoundError,
)
from uptime_platform.organizations.member_dependencies import (
    get_organization_member_service,
)
from uptime_platform.organizations.member_service import (
    OrganizationMemberResult,
    OrganizationMemberService,
)
from uptime_platform.organizations.schemas import (
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    OrganizationMemberUpdate,
)

router = APIRouter(
    prefix="/api/v1/organization-members",
    tags=["organization members"],
)


def _to_response(
    result: OrganizationMemberResult,
) -> OrganizationMemberResponse:
    return OrganizationMemberResponse(
        user_id=result.user.id,
        email=result.user.email,
        role=result.membership.role,
        created_at=result.membership.created_at,
    )


@router.get(
    "",
    response_model=list[OrganizationMemberResponse],
)
async def list_members(
    service: Annotated[
        OrganizationMemberService,
        Depends(get_organization_member_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> list[OrganizationMemberResponse]:
    members = await service.get_all()

    return [_to_response(member) for member in members]


@router.post(
    "",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    data: OrganizationMemberCreate,
    service: Annotated[
        OrganizationMemberService,
        Depends(get_organization_member_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> OrganizationMemberResponse:
    try:
        result = await service.add(
            email=str(data.email),
            role=data.role,
        )
    except OrganizationUserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc
    except OrganizationMemberAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("User is already a member of this organization"),
        ) from exc
    except OrganizationMemberPermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        ) from exc

    return _to_response(result)


@router.patch(
    "/{user_id}",
    response_model=OrganizationMemberResponse,
)
async def update_member(
    user_id: UUID,
    data: OrganizationMemberUpdate,
    service: Annotated[
        OrganizationMemberService,
        Depends(get_organization_member_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> OrganizationMemberResponse:
    try:
        result = await service.update_role(
            user_id=user_id,
            role=data.role,
        )
    except OrganizationMemberNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization member not found",
        ) from exc
    except OrganizationMemberPermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        ) from exc
    except LastOrganizationOwnerError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("The last organization owner cannot be demoted"),
        ) from exc

    return _to_response(result)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    user_id: UUID,
    service: Annotated[
        OrganizationMemberService,
        Depends(get_organization_member_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> Response:
    try:
        await service.delete(user_id)
    except OrganizationMemberNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization member not found",
        ) from exc
    except OrganizationMemberPermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        ) from exc
    except LastOrganizationOwnerError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("The last organization owner cannot be removed"),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
