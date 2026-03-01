from equiny.core.shared.domain.errors.auth_error import AuthError


class InvalidEmailVerificationTokenError(AuthError):
    def __init__(self) -> None:
        super().__init__('Token de verificação de email inválido ou expirado')
