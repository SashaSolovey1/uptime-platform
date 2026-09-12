from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.auth.config import (
    AuthSettings,
    get_auth_settings,
)
from uptime_platform.auth.dependencies import (
    get_token_service,
)
from uptime_platform.auth.refresh_protocols import (
    RefreshSessionRepositoryProtocol,
)
from uptime_platform.auth.refresh_repository import (
    SqlAlchemyRefreshSessionRepository,
)
from uptime_platform.auth.refresh_service import (
    RefreshSessionService,
)
from uptime_platform.auth.token_service import (
    TokenService,
)
from uptime_platform.db.session import (
    get_db_session,
)


def get_refresh_session_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> RefreshSessionRepositoryProtocol:
    return SqlAlchemyRefreshSessionRepository(session)


def get_refresh_session_service(
    repository: Annotated[
        RefreshSessionRepositoryProtocol,
        Depends(get_refresh_session_repository),
    ],
    token_service: Annotated[
        TokenService,
        Depends(get_token_service),
    ],
    settings: Annotated[
        AuthSettings,
        Depends(get_auth_settings),
    ],
) -> RefreshSessionService:
    return RefreshSessionService(
        repository=repository,
        token_service=token_service,
        hash_secret=(settings.refresh_token_hash_secret.get_secret_value()),
        ttl_days=settings.refresh_token_ttl_days,
    )
