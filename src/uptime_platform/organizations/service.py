from datetime import UTC, datetime
from uuid import UUID, uuid4

from uptime_platform.organizations.entities import (
    Membership,
    Organization,
    OrganizationAccess,
    OrganizationRole,
)
from uptime_platform.organizations.protocols import (
    MembershipRepositoryProtocol,
    OrganizationRepositoryProtocol,
)
from uptime_platform.organizations.schemas import (
    OrganizationCreate,
)


class OrganizationService:
    def __init__(
        self,
        organization_repository: OrganizationRepositoryProtocol,
        membership_repository: MembershipRepositoryProtocol,
    ) -> None:
        self._organization_repository = organization_repository
        self._membership_repository = membership_repository

    async def create(
        self,
        user_id: UUID,
        data: OrganizationCreate,
    ) -> OrganizationAccess:
        now = datetime.now(UTC)

        organization = Organization(
            id=uuid4(),
            name=data.name,
            created_at=now,
        )

        membership = Membership(
            id=uuid4(),
            organization_id=organization.id,
            user_id=user_id,
            role=OrganizationRole.OWNER,
            created_at=now,
        )

        organization = await self._organization_repository.create(organization)

        membership = await self._membership_repository.create(membership)

        return OrganizationAccess(
            organization=organization,
            membership=membership,
        )

    async def get_for_user(
        self,
        user_id: UUID,
    ) -> list[OrganizationAccess]:
        memberships = await self._membership_repository.get_by_user_id(user_id)

        accesses: list[OrganizationAccess] = []

        for membership in memberships:
            organization = await self._organization_repository.get_by_id(
                membership.organization_id
            )

            if organization is None:
                continue

            accesses.append(
                OrganizationAccess(
                    organization=organization,
                    membership=membership,
                )
            )

        accesses.sort(key=lambda access: access.organization.created_at)

        return accesses
