from pydantic import BaseModel
from equiny.core.profiling.domain.structures.dtos import LocationDto


class LocationSchema(BaseModel):
    state: str
    city: str
    latitude: float
    longitude: float

    def to_dto(self) -> LocationDto:
        return LocationDto(
            state=self.state,
            city=self.city,
            latitude=self.latitude,
            longitude=self.longitude,
        )
