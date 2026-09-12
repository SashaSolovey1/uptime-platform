from datetime import UTC, datetime
from uuid import uuid4

import pytest

from uptime_platform.organizations.entities import (
    Membership,
    OrganizationRole,
)
from uptime_platform.organizations.exceptions import (
    LastOrganizationOwnerError,
    OrganizationMemberPermissionError,
)
from uptime_platform.organizations.in_memory_repository import (
    InMemoryMembershipRepository,
)
from uptime_platform.organizations.member_service import (
    OrganizationMemberService,
)
from uptime_platform.users.entities import User
from uptime_platform.users.in_memory_repository import (
    InMemoryUserRepository,
)

pytestmark = pytest.mark.anyio


async def test_owner_can_add_admin() -> None:
    organization_id = uuid4()
    owner_id = uuid4()

    memberships = InMemoryMembershipRepository()
    users = InMemoryUserRepository()

    user = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash="not-used",
        created_at=datetime.now(UTC),
    )

    await users.create(user)

    service = OrganizationMemberService(
        membership_repository=memberships,
        user_repository=users,
        organization_id=organization_id,
        actor_user_id=owner_id,
        actor_role=OrganizationRole.OWNER,
    )

    result = await service.add(
        email=user.email,
        role=OrganizationRole.ADMIN,
    )

    assert result.user == user
    assert result.membership.role is OrganizationRole.ADMIN


async def test_admin_cannot_add_owner() -> None:
    organization_id = uuid4()

    memberships = InMemoryMembershipRepository()
    users = InMemoryUserRepository()

    user = User(
        id=uuid4(),
        email="owner@example.com",
        password_hash="not-used",
        created_at=datetime.now(UTC),
    )

    await users.create(user)

    service = OrganizationMemberService(
        membership_repository=memberships,
        user_repository=users,
        organization_id=organization_id,
        actor_user_id=uuid4(),
        actor_role=OrganizationRole.ADMIN,
    )

    with pytest.raises(OrganizationMemberPermissionError):
        await service.add(
            email=user.email,
            role=OrganizationRole.OWNER,
        )


async def test_last_owner_cannot_be_removed() -> None:
    organization_id = uuid4()
    owner_id = uuid4()

    memberships = InMemoryMembershipRepository()
    users = InMemoryUserRepository()

    owner = User(
        id=owner_id,
        email="owner@example.com",
        password_hash="not-used",
        created_at=datetime.now(UTC),
    )

    await users.create(owner)

    membership = Membership(
        id=uuid4(),
        organization_id=organization_id,
        user_id=owner.id,
        role=OrganizationRole.OWNER,
        created_at=datetime.now(UTC),
    )

    await memberships.create(membership)

    service = OrganizationMemberService(
        membership_repository=memberships,
        user_repository=users,
        organization_id=organization_id,
        actor_user_id=owner.id,
        actor_role=OrganizationRole.OWNER,
    )

    with pytest.raises(LastOrganizationOwnerError):
        await service.delete(owner.id)
