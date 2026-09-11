from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class OrganizationRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


@dataclass(frozen=True, slots=True)
class Organization:
    id: UUID
    name: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Membership:
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrganizationRole
    created_at: datetime


@dataclass(frozen=True, slots=True)
class OrganizationAccess:
    organization: Organization
    membership: Membership
