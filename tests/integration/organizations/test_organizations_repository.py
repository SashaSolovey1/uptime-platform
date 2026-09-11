from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.organizations.entities import (
    Membership,
    Organization,
    OrganizationRole,
)
from uptime_platform.organizations.sqlalchemy_repository import (
    SqlAlchemyMembershipRepository,
    SqlAlchemyOrganizationRepository,
)
from uptime_platform.users.entities import User
from uptime_platform.users.sqlalchemy_repository import (
    SqlAlchemyUserRepository,
)

pytestmark = pytest.mark.anyio


async def test_create_and_get_organization(
    db_session: AsyncSession,
) -> None:
    repository = SqlAlchemyOrganizationRepository(db_session)

    organization = Organization(
        id=uuid4(),
        name="Acme",
        created_at=datetime.now(UTC),
    )

    created = await repository.create(organization)

    found = await repository.get_by_id(organization.id)

    assert created == organization
    assert found == organization


async def test_create_and_get_membership(
    db_session: AsyncSession,
) -> None:
    user_repository = SqlAlchemyUserRepository(db_session)
    organization_repository = SqlAlchemyOrganizationRepository(db_session)
    membership_repository = SqlAlchemyMembershipRepository(db_session)

    now = datetime.now(UTC)

    user = User(
        id=uuid4(),
        email=f"{uuid4()}@example.com",
        password_hash="hashed-password",
        created_at=now,
    )

    organization = Organization(
        id=uuid4(),
        name="Acme",
        created_at=now,
    )

    await user_repository.create(user)
    await organization_repository.create(organization)

    membership = Membership(
        id=uuid4(),
        organization_id=organization.id,
        user_id=user.id,
        role=OrganizationRole.OWNER,
        created_at=now,
    )

    created = await membership_repository.create(membership)

    found = await membership_repository.get_by_user_and_organization(
        user_id=user.id,
        organization_id=organization.id,
    )

    assert created == membership
    assert found == membership


async def test_get_memberships_by_user(
    db_session: AsyncSession,
) -> None:
    user_repository = SqlAlchemyUserRepository(db_session)
    organization_repository = SqlAlchemyOrganizationRepository(db_session)
    membership_repository = SqlAlchemyMembershipRepository(db_session)

    now = datetime.now(UTC)

    user = User(
        id=uuid4(),
        email=f"{uuid4()}@example.com",
        password_hash="hashed-password",
        created_at=now,
    )

    first_organization = Organization(
        id=uuid4(),
        name="First",
        created_at=now,
    )

    second_organization = Organization(
        id=uuid4(),
        name="Second",
        created_at=now,
    )

    await user_repository.create(user)

    await organization_repository.create(first_organization)
    await organization_repository.create(second_organization)

    first_membership = Membership(
        id=uuid4(),
        organization_id=first_organization.id,
        user_id=user.id,
        role=OrganizationRole.OWNER,
        created_at=now,
    )

    second_membership = Membership(
        id=uuid4(),
        organization_id=second_organization.id,
        user_id=user.id,
        role=OrganizationRole.VIEWER,
        created_at=now,
    )

    await membership_repository.create(first_membership)
    await membership_repository.create(second_membership)

    memberships = await membership_repository.get_by_user_id(user.id)

    assert {membership.id for membership in memberships} == {
        first_membership.id,
        second_membership.id,
    }
