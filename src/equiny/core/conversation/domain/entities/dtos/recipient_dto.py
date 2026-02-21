from equiny.core.shared.domain.decorators import dto
from equiny.core.shared.domain.structures.dtos.image_dto import ImageDto


@dto
class RecipientDto:
    id: str
    name: str | None = None
    avatar: ImageDto | None = None
