from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from uptime_platform.auth.dependencies import (
    get_auth_service,
    get_current_user,
    get_token_service,
)
from uptime_platform.auth.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from uptime_platform.auth.schemas import (
    LoginRequest,
    MeResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from uptime_platform.auth.service import AuthService
from uptime_platform.auth.token_service import (
    TokenService,
)
from uptime_platform.users.entities import User

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
)
async def register(
    data: RegisterRequest,
    service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
) -> RegisterResponse:
    try:
        result = await service.register(data)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return RegisterResponse(
        user_id=result.user.id,
        email=result.user.email,
        organization_id=result.organization.id,
        organization_name=result.organization.name,
        role=result.membership.role,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
    token_service: Annotated[
        TokenService,
        Depends(get_token_service),
    ],
) -> TokenResponse:
    try:
        user = await service.login(data)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    token = token_service.create_access_token(user.id)

    return TokenResponse(
        access_token=token,
    )


@router.get(
    "/me",
    response_model=MeResponse,
)
async def me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> MeResponse:
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
    )
