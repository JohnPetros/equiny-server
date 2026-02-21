from equiny.core.shared.domain.errors.not_found_error import NotFoundError


class ChatNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__('Chat não encontrado')
