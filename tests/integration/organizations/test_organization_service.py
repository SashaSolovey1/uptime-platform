from uuid import uuid4

import pytest

from uptime_platform.organizations.entities import (
    OrganizationRole,
)
from uptime_platform.organizations.in_memory_repository import (
    InMemoryMembershipRepository,
    InMemoryOrganizationRepository,
)
from uptime_platform.organizations.schemas import (
    OrganizationCreate,
)
from uptime_platform.organizations.service import (
    OrganizationService,
)

pytestmark = pytest.mark.anyio


def make_service() -> tuple[
    OrganizationService,
    InMemoryOrganizationRepository,
    InMemoryMembershipRepository,
]:
    organization_repository = InMemoryOrganizationRepository()

    membership_repository = InMemoryMembershipRepository()

    service = OrganizationService(
        organization_repository=organization_repository,
        membership_repository=membership_repository,
    )

    return (
        service,
        organization_repository,
        membership_repository,
    )


async def test_create_organization_creates_owner_membership() -> None:
    (
        service,
        organization_repository,
        membership_repository,
    ) = make_service()

    user_id = uuid4()

    result = await service.create(
        user_id=user_id,
        data=OrganizationCreate(
            name="Acme",
        ),
    )

    assert result.organization.name == "Acme"

    assert result.membership.organization_id == result.organization.id

    assert result.membership.user_id == user_id

    assert result.membership.role is OrganizationRole.OWNER

    stored_organization = await organization_repository.get_by_id(
        result.organization.id
    )

    assert stored_organization == result.organization

    stored_membership = await membership_repository.get_by_user_and_organization(
        user_id=user_id,
        organization_id=result.organization.id,
    )

    assert stored_membership == result.membership


async def test_get_organizations_for_user() -> None:
    (
        service,
        _,
        _,
    ) = make_service()

    first_user_id = uuid4()
    second_user_id = uuid4()

    first = await service.create(
        first_user_id,
        OrganizationCreate(
            name="First",
        ),
    )

    second = await service.create(
        first_user_id,
        OrganizationCreate(
            name="Second",
        ),
    )

    await service.create(
        second_user_id,
        OrganizationCreate(
            name="Other User",
        ),
    )

    result = await service.get_for_user(first_user_id)

    assert result == [
        first,
        second,
    ]
