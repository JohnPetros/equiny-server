from datetime import datetime

from equiny.core.shared.domain.decorators import dto
from equiny.core.profiling.domain.entities.dtos.horse_dto import HorseDto


@dto
class HorseMatchDto:
    horse: HorseDto
    created_at: datetime
