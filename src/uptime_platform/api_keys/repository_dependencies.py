from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.api_keys.protocols import (
    ApiKeyRepositoryProtocol,
)
from uptime_platform.api_keys.sqlalchemy_repository import (
    SqlAlchemyApiKeyRepository,
)
from uptime_platform.db.session import (
    get_db_session,
)


def get_api_key_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> ApiKeyRepositoryProtocol:
    return SqlAlchemyApiKeyRepository(session)
