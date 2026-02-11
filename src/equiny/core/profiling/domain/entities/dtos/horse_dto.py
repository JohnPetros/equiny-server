from equiny.core.shared.domain.decorators import dto


@dto
class HorseDto:
    id: str | None = None
    name: str
    birth_month: int
    birth_year: int
    breed: str
