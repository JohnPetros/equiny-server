from equiny.core.shared.domain.errors.forbidden_error import ForbiddenError


class ChatNotAllowedError(ForbiddenError):
    def __init__(self) -> None:
        super().__init__('Chat não permitido.')
