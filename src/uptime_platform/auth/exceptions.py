class EmailAlreadyRegisteredError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


class InvalidAccessTokenError(ValueError):
    pass


class InvalidRefreshTokenError(Exception):
    pass
