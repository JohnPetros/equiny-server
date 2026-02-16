from equiny.core.shared.domain.decorators import dto
from equiny.core.profiling.domain.structures.dtos import LocationDto


@dto
class HorseDto:
    id: str | None = None
    name: str
    birth_month: int
    birth_year: int
    breed: str
    sex: str
    height: float
    location: LocationDto
