from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from uptime_platform.api_keys.dependencies import (
    get_api_key_service,
)
from uptime_platform.api_keys.schemas import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
)
from uptime_platform.api_keys.service import (
    ApiKeyService,
)
from uptime_platform.auth.dependencies import (
    require_admin,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)

router = APIRouter(
    prefix="/api/v1/api-keys",
    tags=["api keys"],
)


@router.post(
    "",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_api_key(
    data: ApiKeyCreate,
    service: Annotated[
        ApiKeyService,
        Depends(get_api_key_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> ApiKeyCreatedResponse:
    result = await service.create(data)

    api_key = result.api_key

    return ApiKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        key=result.plaintext_key,
    )


@router.get(
    "",
    response_model=list[ApiKeyResponse],
)
async def list_api_keys(
    service: Annotated[
        ApiKeyService,
        Depends(get_api_key_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> list[ApiKeyResponse]:
    api_keys = await service.get_all()

    return [
        ApiKeyResponse(
            id=api_key.id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            created_at=api_key.created_at,
            last_used_at=api_key.last_used_at,
        )
        for api_key in api_keys
    ]


@router.get(
    "/{api_key_id}",
    response_model=ApiKeyResponse,
)
async def get_api_key(
    api_key_id: UUID,
    service: Annotated[
        ApiKeyService,
        Depends(get_api_key_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> ApiKeyResponse:
    api_key = await service.get_by_id(api_key_id)

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return ApiKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
    )


@router.delete(
    "/{api_key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_api_key(
    api_key_id: UUID,
    service: Annotated[
        ApiKeyService,
        Depends(get_api_key_service),
    ],
    _context: Annotated[
        OrganizationContext,
        Depends(require_admin),
    ],
) -> Response:
    deleted = await service.delete(api_key_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
