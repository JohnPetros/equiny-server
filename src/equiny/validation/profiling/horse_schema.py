from datetime import datetime
from pydantic import BaseModel, Field

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.structures import BreedValue
from equiny.validation.shared import NameSchema


class HorseSchema(BaseModel):
    name: NameSchema
    birth_month: int = Field(ge=1, le=12)
    birth_year: int = Field(ge=1900, le=datetime.now().year)
    breed: BreedValue

    def to_dto(self) -> HorseDto:
        return HorseDto(
            name=self.name,
            birth_month=self.birth_month,
            birth_year=self.birth_year,
            breed=self.breed.value,
        )
