from equiny.core.shared.domain.decorators.dto import dto


@dto
class LocationDto:
    city: str
    state: str
    latitude: float
    longitude: float
