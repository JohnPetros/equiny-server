from equiny.core.shared.domain.errors.conflict_error import ConflictError


class AccountAlreadyVerifiedError(ConflictError):
    def __init__(self) -> None:
        super().__init__('Esta conta já foi verificada')
