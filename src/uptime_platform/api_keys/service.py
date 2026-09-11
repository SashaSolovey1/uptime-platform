from datetime import UTC, datetime
from uuid import UUID, uuid4

from uptime_platform.api_keys.entities import (
    ApiKey,
    ApiKeyCreationResult,
)
from uptime_platform.api_keys.protocols import (
    ApiKeyRepositoryProtocol,
)
from uptime_platform.api_keys.schemas import (
    ApiKeyCreate,
)
from uptime_platform.api_keys.security import (
    generate_api_key,
    get_api_key_prefix,
    hash_api_key,
)


class ApiKeyService:
    def __init__(
        self,
        repository: ApiKeyRepositoryProtocol,
        organization_id: UUID,
    ) -> None:
        self._repository = repository
        self._organization_id = organization_id

    async def create(
        self,
        data: ApiKeyCreate,
    ) -> ApiKeyCreationResult:
        plaintext_key = generate_api_key()

        api_key = ApiKey(
            id=uuid4(),
            organization_id=self._organization_id,
            name=data.name,
            key_hash=hash_api_key(plaintext_key),
            key_prefix=get_api_key_prefix(plaintext_key),
            created_at=datetime.now(UTC),
            last_used_at=None,
        )

        api_key = await self._repository.create(api_key)

        return ApiKeyCreationResult(
            api_key=api_key,
            plaintext_key=plaintext_key,
        )

    async def get_all(
        self,
    ) -> list[ApiKey]:
        return await self._repository.get_all(self._organization_id)

    async def get_by_id(
        self,
        api_key_id: UUID,
    ) -> ApiKey | None:
        return await self._repository.get_by_id(
            api_key_id,
            self._organization_id,
        )

    async def delete(
        self,
        api_key_id: UUID,
    ) -> bool:
        return await self._repository.delete(
            api_key_id,
            self._organization_id,
        )
