from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt import InvalidTokenError as PyJWTInvalidTokenError

from uptime_platform.auth.exceptions import (
    InvalidAccessTokenError,
)


class TokenService:
    def __init__(
        self,
        secret: str,
        algorithm: str,
        access_token_ttl_minutes: int,
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._access_token_ttl_minutes = access_token_ttl_minutes

    def create_access_token(
        self,
        user_id: UUID,
    ) -> str:
        now = datetime.now(UTC)

        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self._access_token_ttl_minutes),
        }

        return jwt.encode(
            payload,
            self._secret,
            algorithm=self._algorithm,
        )

    def get_user_id(
        self,
        token: str,
    ) -> UUID:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[
                    self._algorithm,
                ],
                options={
                    "require": [
                        "sub",
                        "iat",
                        "exp",
                    ]
                },
            )

            if payload.get("type") != "access":
                raise InvalidAccessTokenError("Invalid access token")

            return UUID(payload["sub"])

        except (
            PyJWTInvalidTokenError,
            ValueError,
            TypeError,
        ) as exc:
            raise InvalidAccessTokenError("Invalid or expired access token") from exc
