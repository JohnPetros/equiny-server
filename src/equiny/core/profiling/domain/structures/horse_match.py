from typing import TYPE_CHECKING

from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.datetime import Datetime

if TYPE_CHECKING:
    from equiny.core.profiling.domain.entities.horse import Horse


@structure
class HorseMatch(Structure):
    horse: 'Horse'
    created_at: Datetime

    @classmethod
    def create(cls, dto: HorseMatchDto) -> 'HorseMatch':
        from equiny.core.profiling.domain.entities.horse import Horse

        return cls(
            horse=Horse.create(dto.horse),
            created_at=Datetime.create(dto.created_at),
        )

    @property
    def dto(self) -> HorseMatchDto:
        return HorseMatchDto(
            horse=self.horse.dto,
            created_at=self.created_at.value,
        )
