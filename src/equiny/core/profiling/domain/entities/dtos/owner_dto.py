from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.shared.domain.decorators.dto import dto


@dto
class OwnerDto:
    id: str | None = None
    name: str
    email: str
    account_id: str
    bio: str | None = None
    phone: str | None = None
    avatar: ImageDto | None = None
    has_completed_onboarding: bool
