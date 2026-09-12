from typing import Annotated

from fastapi import Depends

from uptime_platform.auth.dependencies import (
    get_membership_repository,
    get_organization_context,
    get_user_repository,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.organizations.member_service import (
    OrganizationMemberService,
)
from uptime_platform.organizations.protocols import (
    MembershipRepositoryProtocol,
)
from uptime_platform.users.protocols import (
    UserRepositoryProtocol,
)


def get_organization_member_service(
    membership_repository: Annotated[
        MembershipRepositoryProtocol,
        Depends(get_membership_repository),
    ],
    user_repository: Annotated[
        UserRepositoryProtocol,
        Depends(get_user_repository),
    ],
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
) -> OrganizationMemberService:
    actor_user_id = context.user.id if context.user is not None else None

    return OrganizationMemberService(
        membership_repository=membership_repository,
        user_repository=user_repository,
        organization_id=context.organization.id,
        actor_user_id=actor_user_id,
        actor_role=context.role,
    )
