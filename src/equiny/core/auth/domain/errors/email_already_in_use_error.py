from equiny.core.shared.domain.errors.conflict_error import ConflictError


class EmailAlreadyInUseError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__(f'Email {email} already in use')
