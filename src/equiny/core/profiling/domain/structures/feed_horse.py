from equiny.core.profiling.domain.structures.dtos.feed_horse_dto import FeedHorseDto
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.structures.gallery import Gallery


@structure
class FeedHorse(Structure):
    horse: Horse
    gallery: Gallery

    @classmethod
    def create(cls, dto: FeedHorseDto) -> 'FeedHorse':
        return cls(horse=Horse.create(dto.horse), gallery=Gallery.create(dto.gallery))

    @property
    def dto(self) -> FeedHorseDto:
        return FeedHorseDto(
            horse=self.horse.dto,
            gallery=self.gallery.dto,
        )
