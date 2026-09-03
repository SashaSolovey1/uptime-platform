import hashlib
import hmac


def create_webhook_signature(
    secret: str,
    timestamp: str,
    body: bytes,
) -> str:
    signed_payload = timestamp.encode("utf-8") + b"." + body

    digest = hmac.new(
        key=secret.encode("utf-8"),
        msg=signed_payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return f"sha256={digest}"
