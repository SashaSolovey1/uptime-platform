from fastapi import Response

from uptime_platform.auth.config import (
    AuthSettings,
)

REFRESH_COOKIE_PATH = "/api/v1/auth"
SECONDS_PER_DAY = 24 * 60 * 60


def set_refresh_cookie(
    response: Response,
    refresh_token: str,
    settings: AuthSettings,
) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        max_age=(settings.refresh_token_ttl_days * SECONDS_PER_DAY),
        path=REFRESH_COOKIE_PATH,
        secure=settings.refresh_cookie_secure,
        httponly=True,
        samesite=settings.refresh_cookie_samesite,
    )


def clear_refresh_cookie(
    response: Response,
    settings: AuthSettings,
) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=REFRESH_COOKIE_PATH,
    )
