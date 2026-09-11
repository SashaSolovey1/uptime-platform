from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ApiKey:
    id: UUID
    organization_id: UUID
    name: str
    key_hash: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ApiKeyCreationResult:
    api_key: ApiKey
    plaintext_key: str
