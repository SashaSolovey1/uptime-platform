from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from uptime_platform.organizations.entities import (
    OrganizationRole,
)


class OrganizationCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    role: OrganizationRole
    created_at: datetime


class OrganizationMemberCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    email: EmailStr
    role: OrganizationRole


class OrganizationMemberUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    role: OrganizationRole


class OrganizationMemberResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    role: OrganizationRole
    created_at: datetime
