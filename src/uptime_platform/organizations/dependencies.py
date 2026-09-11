from typing import Annotated

from fastapi import Depends

from uptime_platform.auth.dependencies import (
    get_membership_repository,
    get_organization_repository,
)
from uptime_platform.organizations.protocols import (
    MembershipRepositoryProtocol,
    OrganizationRepositoryProtocol,
)
from uptime_platform.organizations.service import (
    OrganizationService,
)


def get_organization_service(
    organization_repository: Annotated[
        OrganizationRepositoryProtocol,
        Depends(get_organization_repository),
    ],
    membership_repository: Annotated[
        MembershipRepositoryProtocol,
        Depends(get_membership_repository),
    ],
) -> OrganizationService:
    return OrganizationService(
        organization_repository=organization_repository,
        membership_repository=membership_repository,
    )
