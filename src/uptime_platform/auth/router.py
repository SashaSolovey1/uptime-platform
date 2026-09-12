from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse

from uptime_platform.auth.config import (
    AuthSettings,
    get_auth_settings,
)
from uptime_platform.auth.cookies import (
    clear_refresh_cookie,
    set_refresh_cookie,
)
from uptime_platform.auth.dependencies import (
    get_auth_service,
    get_current_user,
)
from uptime_platform.auth.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from uptime_platform.auth.refresh_dependencies import (
    get_refresh_session_service,
)
from uptime_platform.auth.refresh_service import (
    RefreshSessionService,
)
from uptime_platform.auth.schemas import (
    LoginRequest,
    MeResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from uptime_platform.auth.service import AuthService
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
    response: Response,
    service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
    refresh_service: Annotated[
        RefreshSessionService,
        Depends(get_refresh_session_service),
    ],
    settings: Annotated[
        AuthSettings,
        Depends(get_auth_settings),
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

    pair = await refresh_service.issue(user.id)

    set_refresh_cookie(
        response,
        pair.refresh_token,
        settings,
    )

    response.headers["Cache-Control"] = "no-store"

    return TokenResponse(
        access_token=pair.access_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    request: Request,
    response: Response,
    refresh_service: Annotated[
        RefreshSessionService,
        Depends(get_refresh_session_service),
    ],
    settings: Annotated[
        AuthSettings,
        Depends(get_auth_settings),
    ],
) -> TokenResponse | Response:
    refresh_token = request.cookies.get(settings.refresh_cookie_name)

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    try:
        pair = await refresh_service.refresh(refresh_token)
    except InvalidRefreshTokenError:
        error_response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": ("Invalid or expired refresh token"),
            },
        )

        clear_refresh_cookie(
            error_response,
            settings,
        )

        return error_response

    set_refresh_cookie(
        response,
        pair.refresh_token,
        settings,
    )

    response.headers["Cache-Control"] = "no-store"

    return TokenResponse(
        access_token=pair.access_token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    request: Request,
    refresh_service: Annotated[
        RefreshSessionService,
        Depends(get_refresh_session_service),
    ],
    settings: Annotated[
        AuthSettings,
        Depends(get_auth_settings),
    ],
) -> Response:
    refresh_token = request.cookies.get(settings.refresh_cookie_name)

    if refresh_token is not None:
        await refresh_service.revoke(refresh_token)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    clear_refresh_cookie(
        response,
        settings,
    )

    return response


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
