from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.auth.dependencies import get_organization_context
from uptime_platform.auth.entities import OrganizationContext
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
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
) -> NotificationDestinationService:
    return NotificationDestinationService(
        repository=repository,
        organization_id=context.organization.id,
    )
