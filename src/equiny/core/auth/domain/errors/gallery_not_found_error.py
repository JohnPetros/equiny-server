from equiny.core.shared.domain.errors.not_found_error import NotFoundError


class GalleryNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__('Galeria não encontrada')
