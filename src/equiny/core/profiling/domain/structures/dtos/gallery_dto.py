from equiny.core.shared.domain.decorators.dto import dto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto


@dto
class GalleryDto:
    images: list[ImageDto]
