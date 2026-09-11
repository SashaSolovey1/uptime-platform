from typing import Protocol
from uuid import UUID

from uptime_platform.users.entities import User


class UserRepositoryProtocol(Protocol):
    async def create(
        self,
        user: User,
    ) -> User: ...

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None: ...

    async def get_by_email(
        self,
        email: str,
    ) -> User | None: ...
