from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.auth.dependencies import get_organization_context
from uptime_platform.auth.entities import OrganizationContext
from uptime_platform.db.session import get_db_session
from uptime_platform.monitors.sqlalchemy_repository import (
    SqlAlchemyMonitorRepository,
)
from uptime_platform.status_pages.service import (
    PublicStatusPageService,
    StatusPageService,
)
from uptime_platform.status_pages.sqlalchemy_repository import (
    SqlAlchemyStatusPageRepository,
)


def get_status_page_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
) -> StatusPageService:
    return StatusPageService(
        repository=SqlAlchemyStatusPageRepository(session),
        monitor_repository=SqlAlchemyMonitorRepository(session),
        organization_id=context.organization.id,
    )


def get_public_status_page_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> PublicStatusPageService:
    return PublicStatusPageService(
        repository=SqlAlchemyStatusPageRepository(session),
        monitor_repository=SqlAlchemyMonitorRepository(session),
    )
