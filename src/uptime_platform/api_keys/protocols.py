from datetime import datetime
from typing import Protocol
from uuid import UUID

from uptime_platform.api_keys.entities import ApiKey


class ApiKeyRepositoryProtocol(Protocol):
    async def create(
        self,
        api_key: ApiKey,
    ) -> ApiKey: ...

    async def get_by_id(
        self,
        api_key_id: UUID,
        organization_id: UUID,
    ) -> ApiKey | None: ...

    async def get_by_hash(
        self,
        key_hash: str,
    ) -> ApiKey | None: ...

    async def get_all(
        self,
        organization_id: UUID,
    ) -> list[ApiKey]: ...

    async def delete(
        self,
        api_key_id: UUID,
        organization_id: UUID,
    ) -> bool: ...

    async def update_last_used(
        self,
        api_key_id: UUID,
        last_used_at: datetime,
    ) -> bool: ...
