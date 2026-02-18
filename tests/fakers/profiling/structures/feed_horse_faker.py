from faker import Faker

from equiny.core.profiling.domain.structures.dtos import (
    FeedHorseDto,
    GalleryDto,
)
from equiny.core.profiling.domain.structures.feed_horse import FeedHorse
from equiny.fakers.profiling.entities.horses_faker import HorsesFaker
from equiny.fakers.profiling.structures.image_faker import ImageFaker
from equiny.core.profiling.domain.entities.dtos.horse_dto import HorseDto


class FeedHorseFaker:
    _faker = Faker()

    @staticmethod
    def fake(
        horse_dto: HorseDto | None = None,
        gallery_dto: GalleryDto | None = None,
    ) -> FeedHorse:
        return FeedHorse.create(
            FeedHorseFaker.fake_dto(horse_dto=horse_dto, gallery_dto=gallery_dto)
        )

    @staticmethod
    def fake_dto(
        horse_dto: HorseDto | None = None,
        gallery_dto: GalleryDto | None = None,
    ) -> FeedHorseDto:
        images = [
            ImageFaker.fake_dto()
            for _ in range(FeedHorseFaker._faker.random_int(min=1, max=5))
        ]
        gallery_dto = gallery_dto or GalleryDto(images=images)
        return FeedHorseDto(
            horse=horse_dto or HorsesFaker.fake_dto(),
            gallery=gallery_dto,
        )
