from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.datetime import Datetime
from equiny.core.matching.domain.structures.dtos.match_dto import MatchDto


@structure
class Match(Structure):
    horse_a_id: Id
    horse_b_id: Id
    created_at: Datetime

    @classmethod
    def create(cls, dto: MatchDto) -> 'Match':
        return cls(
            horse_a_id=Id.create(dto.horse_a_id),
            horse_b_id=Id.create(dto.horse_b_id),
            created_at=Datetime.create(dto.created_at),
        )

    @property
    def dto(self) -> MatchDto:
        return MatchDto(
            horse_a_id=self.horse_a_id.value,
            horse_b_id=self.horse_b_id.value,
            created_at=self.created_at.value,
        )
