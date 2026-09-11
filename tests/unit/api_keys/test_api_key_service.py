from uuid import uuid4

import pytest

from uptime_platform.api_keys.in_memory_repository import (
    InMemoryApiKeyRepository,
)
from uptime_platform.api_keys.schemas import (
    ApiKeyCreate,
)
from uptime_platform.api_keys.security import (
    hash_api_key,
)
from uptime_platform.api_keys.service import (
    ApiKeyService,
)

pytestmark = pytest.mark.anyio


async def test_create_api_key_stores_only_hash() -> None:
    organization_id = uuid4()

    repository = InMemoryApiKeyRepository()

    service = ApiKeyService(
        repository=repository,
        organization_id=organization_id,
    )

    result = await service.create(
        ApiKeyCreate(
            name="CI",
        )
    )

    assert result.plaintext_key.startswith("upt_")

    assert result.api_key.key_hash == hash_api_key(result.plaintext_key)

    assert result.api_key.key_hash != result.plaintext_key

    assert result.api_key.organization_id == organization_id
    assert result.api_key.name == "CI"
    assert result.api_key.last_used_at is None


async def test_api_keys_are_scoped_to_organization() -> None:
    repository = InMemoryApiKeyRepository()

    first_service = ApiKeyService(
        repository=repository,
        organization_id=uuid4(),
    )

    second_service = ApiKeyService(
        repository=repository,
        organization_id=uuid4(),
    )

    created = await first_service.create(
        ApiKeyCreate(
            name="CI",
        )
    )

    assert await second_service.get_by_id(created.api_key.id) is None

    assert await second_service.get_all() == []
