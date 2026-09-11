from pwdlib import PasswordHash

_password_hasher = PasswordHash.recommended()


def hash_password(
    password: str,
) -> str:
    return _password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return _password_hasher.verify(
        password,
        password_hash,
    )
