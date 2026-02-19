from datetime import datetime

from equiny.core.shared.domain.decorators import dto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.domain.structures.dtos.location_dto import LocationDto


@dto
class HorseMatchDto:
    owner_id: str
    owner_name: str
    owner_avatar: ImageDto
    owner_horse_id: str
    owner_location: LocationDto
    is_viewed: bool
    created_at: datetime
