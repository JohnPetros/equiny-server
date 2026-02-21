from equiny.core.shared.domain.errors.conflict_error import ConflictError


class ChatAlreadyExistsError(ConflictError):
    def __init__(self) -> None:
        super().__init__('Chat já existe')
