from equiny.core.shared.domain.errors.not_found_error import NotFoundError


class MatchNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__('Match não encontrado')
