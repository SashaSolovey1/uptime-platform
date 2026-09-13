from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from uptime_platform.organizations.constants import (
    DEFAULT_ORGANIZATION_ID,
)
from uptime_platform.organizations.models import (
    OrganizationModel,
)


@pytest.fixture(autouse=True)
async def ensure_test_organization(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[None]:
    async with session_factory() as session:
        organization = await session.get(
            OrganizationModel,
            DEFAULT_ORGANIZATION_ID,
        )

        if organization is None:
            session.add(
                OrganizationModel(
                    id=DEFAULT_ORGANIZATION_ID,
                    name="Integration Test Organization",
                    created_at=datetime.now(UTC),
                )
            )

            await session.commit()

    yield
