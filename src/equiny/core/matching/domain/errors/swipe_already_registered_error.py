from equiny.core.shared.domain.errors.conflict_error import ConflictError


class SwipeAlreadyRegisteredError(ConflictError):
    def __init__(self) -> None:
        super().__init__('Swipe já registrado')
