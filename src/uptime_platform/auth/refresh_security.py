import hmac
import secrets

REFRESH_TOKEN_PREFIX = "upr_"


def generate_refresh_token() -> str:
    secret = secrets.token_urlsafe(48)

    return f"{REFRESH_TOKEN_PREFIX}{secret}"


def hash_refresh_token(
    refresh_token: str,
    hash_secret: str,
) -> str:
    return hmac.digest(
        hash_secret.encode("utf-8"),
        refresh_token.encode("utf-8"),
        "sha256",
    ).hex()
