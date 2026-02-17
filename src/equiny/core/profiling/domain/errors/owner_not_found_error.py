from equiny.core.shared.domain.errors import NotFoundError


class OwnerNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__('Dono de cavalo não encontrado')
