from equiny.core.shared.domain.decorators import dto
from equiny.core.profiling.domain.structures.dtos import LocationDto


@dto
class HorseDto:
    id: str | None = None
    name: str
    birth_month: int
    birth_year: int
    description: str | None = None
    breed: str
    sex: str
    height: float
    location: LocationDto
    is_active: bool
