from dataclasses import dataclass

from uptime_platform.api_keys.entities import ApiKey
from uptime_platform.organizations.entities import (
    Membership,
    Organization,
    OrganizationRole,
)
from uptime_platform.users.entities import User


@dataclass(frozen=True, slots=True)
class RegistrationResult:
    user: User
    organization: Organization
    membership: Membership


@dataclass(frozen=True, slots=True)
class OrganizationContext:
    user: User | None
    organization: Organization
    membership: Membership | None
    api_key: ApiKey | None = None

    @property
    def role(self) -> OrganizationRole:
        if self.membership is not None:
            return self.membership.role

        if self.api_key is not None:
            return OrganizationRole.MEMBER

        raise RuntimeError("Organization context has no principal")
