import hmac
import secrets

API_KEY_PREFIX = "upt_"
API_KEY_VISIBLE_PREFIX_LENGTH = 12


def generate_api_key() -> str:
    secret = secrets.token_urlsafe(32)

    return f"{API_KEY_PREFIX}{secret}"


def hash_api_key(
    api_key: str,
    hash_secret: str,
) -> str:
    return hmac.digest(
        hash_secret.encode("utf-8"),
        api_key.encode("utf-8"),
        "sha256",
    ).hex()


def get_api_key_prefix(
    api_key: str,
) -> str:
    return api_key[:API_KEY_VISIBLE_PREFIX_LENGTH]
