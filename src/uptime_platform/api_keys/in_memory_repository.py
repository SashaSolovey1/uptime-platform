from dataclasses import replace
from datetime import datetime
from uuid import UUID

from uptime_platform.api_keys.entities import ApiKey


class InMemoryApiKeyRepository:
    def __init__(self) -> None:
        self._api_keys: dict[UUID, ApiKey] = {}

    async def create(
        self,
        api_key: ApiKey,
    ) -> ApiKey:
        self._api_keys[api_key.id] = api_key

        return api_key

    async def get_by_id(
        self,
        api_key_id: UUID,
        organization_id: UUID,
    ) -> ApiKey | None:
        api_key = self._api_keys.get(api_key_id)

        if api_key is None:
            return None

        if api_key.organization_id != organization_id:
            return None

        return api_key

    async def get_by_hash(
        self,
        key_hash: str,
    ) -> ApiKey | None:
        for api_key in self._api_keys.values():
            if api_key.key_hash == key_hash:
                return api_key

        return None

    async def get_all(
        self,
        organization_id: UUID,
    ) -> list[ApiKey]:
        api_keys = [
            api_key
            for api_key in self._api_keys.values()
            if api_key.organization_id == organization_id
        ]

        return sorted(
            api_keys,
            key=lambda api_key: api_key.created_at,
        )

    async def delete(
        self,
        api_key_id: UUID,
        organization_id: UUID,
    ) -> bool:
        api_key = self._api_keys.get(api_key_id)

        if api_key is None:
            return False

        if api_key.organization_id != organization_id:
            return False

        del self._api_keys[api_key_id]

        return True

    async def update_last_used(
        self,
        api_key_id: UUID,
        last_used_at: datetime,
    ) -> bool:
        api_key = self._api_keys.get(api_key_id)

        if api_key is None:
            return False

        self._api_keys[api_key_id] = replace(
            api_key,
            last_used_at=last_used_at,
        )

        return True
