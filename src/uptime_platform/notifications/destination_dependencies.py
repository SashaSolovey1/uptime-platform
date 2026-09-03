from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.db.session import get_db_session
from uptime_platform.notifications.destination_service import (
    NotificationDestinationService,
)
from uptime_platform.notifications.repository_protocols import (
    NotificationDestinationRepositoryProtocol,
)
from uptime_platform.notifications.sqlalchemy_repository import (
    SqlAlchemyNotificationDestinationRepository,
)


def get_notification_destination_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> NotificationDestinationRepositoryProtocol:
    return SqlAlchemyNotificationDestinationRepository(session)


def get_notification_destination_service(
    repository: Annotated[
        NotificationDestinationRepositoryProtocol,
        Depends(get_notification_destination_repository),
    ],
) -> NotificationDestinationService:
    return NotificationDestinationService(repository)
