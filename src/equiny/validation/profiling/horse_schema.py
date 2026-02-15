from datetime import datetime
from pydantic import BaseModel, Field

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.structures import BreedValue
from equiny.core.profiling.domain.structures.sex import SexValue
from equiny.validation.shared import NameSchema
from equiny.validation.profiling.location_schema import LocationSchema

current_year = datetime.now().year


class HorseSchema(BaseModel):
    name: NameSchema
    birth_month: int = Field(ge=1, le=12)
    birth_year: int = Field(ge=current_year - 20, le=current_year)
    breed: BreedValue
    sex: SexValue
    location: LocationSchema

    def to_dto(self) -> HorseDto:
        return HorseDto(
            name=self.name,
            birth_month=self.birth_month,
            birth_year=self.birth_year,
            breed=self.breed.value,
            sex=self.sex.value,
            location=self.location.to_dto(),
        )
