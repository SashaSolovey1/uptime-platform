from uuid import UUID

from uptime_platform.users.entities import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def create(
        self,
        user: User,
    ) -> User:
        self._users[user.id] = user

        return user

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user

        return None
