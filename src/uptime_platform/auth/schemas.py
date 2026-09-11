from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
)

from uptime_platform.organizations.entities import (
    OrganizationRole,
)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    email: EmailStr

    password: SecretStr = Field(
        min_length=8,
        max_length=128,
    )

    organization_name: str = Field(
        min_length=1,
        max_length=100,
    )


class RegisterResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    organization_id: UUID
    organization_name: str
    role: OrganizationRole


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    email: EmailStr
    password: SecretStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class MeResponse(BaseModel):
    id: UUID
    email: EmailStr
