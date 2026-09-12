from typing import Annotated

from fastapi import Depends

from uptime_platform.api_keys.config import (
    ApiKeySettings,
    get_api_key_settings,
)
from uptime_platform.api_keys.protocols import (
    ApiKeyRepositoryProtocol,
)
from uptime_platform.api_keys.repository_dependencies import (
    get_api_key_repository,
)
from uptime_platform.api_keys.service import (
    ApiKeyService,
)
from uptime_platform.auth.dependencies import (
    get_organization_context,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)


def get_api_key_service(
    repository: Annotated[
        ApiKeyRepositoryProtocol,
        Depends(get_api_key_repository),
    ],
    context: Annotated[
        OrganizationContext,
        Depends(get_organization_context),
    ],
    settings: Annotated[
        ApiKeySettings,
        Depends(get_api_key_settings),
    ],
) -> ApiKeyService:
    return ApiKeyService(
        repository=repository,
        organization_id=context.organization.id,
        hash_secret=(settings.api_key_hash_secret.get_secret_value()),
    )
