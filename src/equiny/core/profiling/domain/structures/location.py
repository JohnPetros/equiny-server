from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.text import Text
from equiny.core.profiling.domain.structures.dtos import LocationDto


@structure
class Location(Structure):
    city: Text
    state: Text

    @classmethod
    def create(cls, dto: LocationDto) -> 'Location':
        return cls(city=Text.create(dto.city), state=Text.create(dto.state))

    @property
    def dto(self) -> LocationDto:
        return LocationDto(city=self.city.value, state=self.state.value)
