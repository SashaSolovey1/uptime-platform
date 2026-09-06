from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from uptime_platform.notifications.entities import (
    NotificationDestination,
    NotificationDestinationConfig,
    TelegramDestinationConfig,
    WebhookDestinationConfig,
)
from uptime_platform.notifications.repository_protocols import (
    NotificationDestinationRepositoryProtocol,
)
from uptime_platform.notifications.schemas import (
    NotificationDestinationCreate,
    NotificationDestinationUpdate,
    TelegramDestinationConfigCreate,
    TelegramDestinationConfigUpdate,
    WebhookDestinationConfigCreate,
    WebhookDestinationConfigUpdate,
)


def _create_config(
    config: (WebhookDestinationConfigCreate | TelegramDestinationConfigCreate),
) -> NotificationDestinationConfig:
    if isinstance(
        config,
        WebhookDestinationConfigCreate,
    ):
        return WebhookDestinationConfig(
            url=str(config.url),
            secret=config.secret,
        )

    if isinstance(
        config,
        TelegramDestinationConfigCreate,
    ):
        return TelegramDestinationConfig(
            bot_token=config.bot_token,
            chat_id=config.chat_id,
        )

    raise TypeError(f"Unsupported destination config: {type(config)}")


def _update_config(
    current: NotificationDestinationConfig,
    update: (WebhookDestinationConfigUpdate | TelegramDestinationConfigUpdate),
) -> NotificationDestinationConfig:
    if isinstance(
        current,
        WebhookDestinationConfig,
    ) and isinstance(
        update,
        WebhookDestinationConfigUpdate,
    ):
        return WebhookDestinationConfig(
            url=(str(update.url) if update.url is not None else current.url),
            secret=(update.secret if update.secret is not None else current.secret),
        )

    if isinstance(
        current,
        TelegramDestinationConfig,
    ) and isinstance(
        update,
        TelegramDestinationConfigUpdate,
    ):
        return TelegramDestinationConfig(
            bot_token=(
                update.bot_token if update.bot_token is not None else current.bot_token
            ),
            chat_id=(update.chat_id if update.chat_id is not None else current.chat_id),
        )

    raise ValueError("Destination config type does not match destination type")


class NotificationDestinationService:
    def __init__(
        self,
        repository: NotificationDestinationRepositoryProtocol,
    ) -> None:
        self._repository = repository

    async def create(
        self,
        data: NotificationDestinationCreate,
    ) -> NotificationDestination:
        destination = NotificationDestination(
            id=uuid4(),
            name=data.name,
            destination_type=data.destination_type,
            enabled=data.enabled,
            config=_create_config(data.config),
            created_at=datetime.now(UTC),
        )

        return await self._repository.create(destination)

    async def get_all(
        self,
    ) -> list[NotificationDestination]:
        return await self._repository.get_all()

    async def get_by_id(
        self,
        destination_id: UUID,
    ) -> NotificationDestination | None:
        return await self._repository.get_by_id(destination_id)

    async def update(
        self,
        destination_id: UUID,
        data: NotificationDestinationUpdate,
    ) -> NotificationDestination | None:
        destination = await self._repository.get_by_id(destination_id)

        if destination is None:
            return None

        config = destination.config

        if data.config is not None:
            config = _update_config(
                current=destination.config,
                update=data.config,
            )

        updated_destination = replace(
            destination,
            name=(data.name if data.name is not None else destination.name),
            enabled=(data.enabled if data.enabled is not None else destination.enabled),
            config=config,
        )

        return await self._repository.update(updated_destination)

    async def delete(
        self,
        destination_id: UUID,
    ) -> bool:
        return await self._repository.delete(destination_id)
