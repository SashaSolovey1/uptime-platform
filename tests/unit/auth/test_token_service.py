from uuid import uuid4

import pytest

from uptime_platform.auth.exceptions import (
    InvalidAccessTokenError,
)
from uptime_platform.auth.token_service import (
    TokenService,
)

TEST_SECRET = "0123456789abcdef0123456789abcdef"
FIRST_SECRET = "11111111111111111111111111111111"
SECOND_SECRET = "22222222222222222222222222222222"


def make_service() -> TokenService:
    return TokenService(
        secret=TEST_SECRET,
        algorithm="HS256",
        access_token_ttl_minutes=60,
    )


def test_access_token_contains_user_id() -> None:
    service = make_service()

    user_id = uuid4()

    token = service.create_access_token(user_id)

    decoded_user_id = service.get_user_id(token)

    assert decoded_user_id == user_id


def test_invalid_access_token_is_rejected() -> None:
    service = make_service()

    with pytest.raises(InvalidAccessTokenError):
        service.get_user_id("this-is-not-a-jwt")


def test_token_signed_with_another_secret_is_rejected() -> None:
    first_service = TokenService(
        secret=FIRST_SECRET,
        algorithm="HS256",
        access_token_ttl_minutes=60,
    )

    second_service = TokenService(
        secret=SECOND_SECRET,
        algorithm="HS256",
        access_token_ttl_minutes=60,
    )

    token = first_service.create_access_token(uuid4())

    with pytest.raises(InvalidAccessTokenError):
        second_service.get_user_id(token)
