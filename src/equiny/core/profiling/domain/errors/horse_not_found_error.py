from equiny.core.shared.domain.errors.not_found_error import NotFoundError


class HorseNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__('Cavalo não encontrado')
