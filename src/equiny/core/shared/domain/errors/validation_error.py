from equiny.core.shared.domain.errors.app_error import AppError


class ValidationError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__('Validation error', message)
