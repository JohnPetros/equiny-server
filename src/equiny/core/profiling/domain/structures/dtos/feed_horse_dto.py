from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.structures.dtos import GalleryDto
from equiny.core.shared.domain.decorators.dto import dto


@dto
class FeedHorseDto:
    horse: HorseDto
    gallery: GalleryDto
