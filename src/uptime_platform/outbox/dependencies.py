from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.db.session import get_db_session
from uptime_platform.outbox.protocols import (
    OutboxRepositoryProtocol,
)
from uptime_platform.outbox.sqlalchemy_repository import (
    SqlAlchemyOutboxRepository,
)


def get_outbox_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> OutboxRepositoryProtocol:
    return SqlAlchemyOutboxRepository(session)
