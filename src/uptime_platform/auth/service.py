from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

from uptime_platform.auth.entities import (
    RegistrationResult,
)
from uptime_platform.auth.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from uptime_platform.auth.schemas import (
    LoginRequest,
    RegisterRequest,
)
from uptime_platform.auth.security import (
    hash_password,
    verify_password,
)
from uptime_platform.organizations.constants import (
    DEFAULT_ORGANIZATION_ID,
)
from uptime_platform.organizations.entities import (
    Membership,
    Organization,
    OrganizationRole,
)
from uptime_platform.organizations.protocols import (
    MembershipRepositoryProtocol,
    OrganizationRepositoryProtocol,
)
from uptime_platform.users.entities import User
from uptime_platform.users.protocols import (
    UserRepositoryProtocol,
)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        organization_repository: OrganizationRepositoryProtocol,
        membership_repository: MembershipRepositoryProtocol,
    ) -> None:
        self._user_repository = user_repository
        self._organization_repository = organization_repository
        self._membership_repository = membership_repository

    async def register(
        self,
        data: RegisterRequest,
    ) -> RegistrationResult:
        email = str(data.email).lower()

        existing_user = await self._user_repository.get_by_email(email)

        if existing_user is not None:
            raise EmailAlreadyRegisteredError("Email is already registered")

        password_hash = hash_password(data.password.get_secret_value())

        now = datetime.now(UTC)

        default_organization = await self._organization_repository.get_by_id_for_update(
            DEFAULT_ORGANIZATION_ID
        )

        default_memberships: list[Membership] = []

        if default_organization is not None:
            default_memberships = (
                await self._membership_repository.get_by_organization_id(
                    DEFAULT_ORGANIZATION_ID
                )
            )

        if default_organization is not None and not default_memberships:
            organization = replace(
                default_organization,
                name=data.organization_name,
            )

            organization = await self._organization_repository.update(organization)

        else:
            organization = Organization(
                id=uuid4(),
                name=data.organization_name,
                created_at=now,
            )

            organization = await self._organization_repository.create(organization)

        user = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            created_at=now,
        )

        user = await self._user_repository.create(user)

        membership = Membership(
            id=uuid4(),
            organization_id=organization.id,
            user_id=user.id,
            role=OrganizationRole.OWNER,
            created_at=now,
        )

        membership = await self._membership_repository.create(membership)

        return RegistrationResult(
            user=user,
            organization=organization,
            membership=membership,
        )

    async def login(
        self,
        data: LoginRequest,
    ) -> User:
        email = str(data.email).lower()

        user = await self._user_repository.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(
            data.password.get_secret_value(),
            user.password_hash,
        ):
            raise InvalidCredentialsError("Invalid email or password")

        return user
