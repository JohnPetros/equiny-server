from equiny.core.shared.domain.errors import AuthError


class InvalidCredentialsError(AuthError):
    def __init__(self) -> None:
        super().__init__('Invalid credentials')
