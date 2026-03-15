from equiny.core.shared.domain.errors import AuthError


class InvalidCredentialsError(AuthError):
    def __init__(self, message: str = 'Credenciais inválidas') -> None:
        super().__init__(message)
