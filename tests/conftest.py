from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from uptime_platform.auth.entities import OrganizationContext
from uptime_platform.checks.models import CheckModel
from uptime_platform.monitors.models import MonitorModel
from uptime_platform.organizations.constants import (
    DEFAULT_ORGANIZATION_ID,
)
from uptime_platform.organizations.entities import (
    Membership,
    Organization,
    OrganizationRole,
)
from uptime_platform.organizations.models import (
    MembershipModel,  # noqa: F401
    OrganizationModel,  # noqa: F401
)
from uptime_platform.users.entities import User
from uptime_platform.users.models import UserModel  # noqa: F401


class TestSettings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    settings = TestSettings()

    engine = create_async_engine(
        settings.database_url,
    )

    factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    try:
        yield factory

    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        await session.execute(delete(CheckModel))
        await session.execute(delete(MonitorModel))
        await session.commit()

        try:
            yield session

        finally:
            await session.rollback()

            await session.execute(delete(CheckModel))
            await session.execute(delete(MonitorModel))
            await session.commit()


@pytest.fixture
def organization_context() -> OrganizationContext:
    now = datetime.now(UTC)

    user = User(
        id=uuid4(),
        email="owner@example.com",
        password_hash="not-used",
        created_at=now,
    )

    organization = Organization(
        id=DEFAULT_ORGANIZATION_ID,
        name="Test Organization",
        created_at=now,
    )

    membership = Membership(
        id=uuid4(),
        organization_id=organization.id,
        user_id=user.id,
        role=OrganizationRole.OWNER,
        created_at=now,
    )

    return OrganizationContext(
        user=user,
        organization=organization,
        membership=membership,
    )
