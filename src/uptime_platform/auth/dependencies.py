from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import (
    Depends,
    Header,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.api_keys.config import (
    ApiKeySettings,
    get_api_key_settings,
)
from uptime_platform.api_keys.protocols import (
    ApiKeyRepositoryProtocol,
)
from uptime_platform.api_keys.repository_dependencies import (
    get_api_key_repository,
)
from uptime_platform.api_keys.security import (
    API_KEY_PREFIX,
    hash_api_key,
)
from uptime_platform.auth.config import (
    AuthSettings,
    get_auth_settings,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.auth.exceptions import (
    InvalidAccessTokenError,
)
from uptime_platform.auth.service import AuthService
from uptime_platform.auth.token_service import (
    TokenService,
)
from uptime_platform.db.session import get_db_session
from uptime_platform.organizations.entities import (
    OrganizationRole,
)
from uptime_platform.organizations.protocols import (
    MembershipRepositoryProtocol,
    OrganizationRepositoryProtocol,
)
from uptime_platform.organizations.sqlalchemy_repository import (
    SqlAlchemyMembershipRepository,
    SqlAlchemyOrganizationRepository,
)
from uptime_platform.users.entities import User
from uptime_platform.users.protocols import (
    UserRepositoryProtocol,
)
from uptime_platform.users.sqlalchemy_repository import (
    SqlAlchemyUserRepository,
)

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_user_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> UserRepositoryProtocol:
    return SqlAlchemyUserRepository(session)


def get_organization_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> OrganizationRepositoryProtocol:
    return SqlAlchemyOrganizationRepository(session)


def get_membership_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> MembershipRepositoryProtocol:
    return SqlAlchemyMembershipRepository(session)


def get_auth_service(
    user_repository: Annotated[
        UserRepositoryProtocol,
        Depends(get_user_repository),
    ],
    organization_repository: Annotated[
        OrganizationRepositoryProtocol,
        Depends(get_organization_repository),
    ],
    membership_repository: Annotated[
        MembershipRepositoryProtocol,
        Depends(get_membership_repository),
    ],
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        organization_repository=organization_repository,
        membership_repository=membership_repository,
    )


def get_token_service(
    settings: Annotated[
        AuthSettings,
        Depends(get_auth_settings),
    ],
) -> TokenService:
    return TokenService(
        secret=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        access_token_ttl_minutes=(settings.jwt_access_token_ttl_minutes),
    )


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    token_service: Annotated[
        TokenService,
        Depends(get_token_service),
    ],
    user_repository: Annotated[
        UserRepositoryProtocol,
        Depends(get_user_repository),
    ],
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id = token_service.get_user_id(credentials.credentials)
    except InvalidAccessTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user


_ROLE_LEVEL = {
    OrganizationRole.VIEWER: 10,
    OrganizationRole.MEMBER: 20,
    OrganizationRole.ADMIN: 30,
    OrganizationRole.OWNER: 40,
}


async def get_organization_context(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    token_service: Annotated[
        TokenService,
        Depends(get_token_service),
    ],
    user_repository: Annotated[
        UserRepositoryProtocol,
        Depends(get_user_repository),
    ],
    organization_repository: Annotated[
        OrganizationRepositoryProtocol,
        Depends(get_organization_repository),
    ],
    membership_repository: Annotated[
        MembershipRepositoryProtocol,
        Depends(get_membership_repository),
    ],
    api_key_repository: Annotated[
        ApiKeyRepositoryProtocol,
        Depends(get_api_key_repository),
    ],
    api_key_settings: Annotated[
        ApiKeySettings,
        Depends(get_api_key_settings),
    ],
    organization_id: Annotated[
        UUID | None,
        Header(alias="X-Organization-ID"),
    ] = None,
) -> OrganizationContext:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    if token.startswith(API_KEY_PREFIX):
        key_hash = hash_api_key(
            token,
            api_key_settings.api_key_hash_secret.get_secret_value(),
        )

        api_key = await api_key_repository.get_by_hash(key_hash)

        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if organization_id is not None and organization_id != api_key.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        organization = await organization_repository.get_by_id(api_key.organization_id)

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        await api_key_repository.update_last_used(
            api_key_id=api_key.id,
            last_used_at=datetime.now(UTC),
        )

        return OrganizationContext(
            user=None,
            organization=organization,
            membership=None,
            api_key=api_key,
        )

    try:
        user_id = token_service.get_user_id(token)
    except InvalidAccessTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="X-Organization-ID header is required",
        )

    membership = await membership_repository.get_by_user_and_organization(
        user_id=user.id,
        organization_id=organization_id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    organization = await organization_repository.get_by_id(organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return OrganizationContext(
        user=user,
        organization=organization,
        membership=membership,
    )


def _require_minimum_role(
    context: OrganizationContext,
    minimum_role: OrganizationRole,
) -> OrganizationContext:
    if _ROLE_LEVEL[context.role] < _ROLE_LEVEL[minimum_role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return context


async def require_member(
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
) -> OrganizationContext:
    return _require_minimum_role(
        context,
        OrganizationRole.MEMBER,
    )


async def require_admin(
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
) -> OrganizationContext:
    return _require_minimum_role(
        context,
        OrganizationRole.ADMIN,
    )


async def require_owner(
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
) -> OrganizationContext:
    return _require_minimum_role(
        context,
        OrganizationRole.OWNER,
    )
