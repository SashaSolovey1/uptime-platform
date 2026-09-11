from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ApiKeyCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )


class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime | None


class ApiKeyCreatedResponse(ApiKeyResponse):
    key: str
