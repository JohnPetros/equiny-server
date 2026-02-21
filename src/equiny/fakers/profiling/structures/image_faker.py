from faker import Faker

from equiny.core.profiling.domain.structures.dtos import ImageDto
from equiny.core.shared.domain.structures.image import Image


class ImageFaker:
    _faker = Faker()

    @staticmethod
    def fake(key: str | None = None, name: str | None = None) -> Image:
        return Image.create(ImageFaker.fake_dto(key=key, name=name))

    @staticmethod
    def fake_dto(key: str | None = None, name: str | None = None) -> ImageDto:
        return ImageDto(
            key=key or ImageFaker._faker.uuid4(),
            name=name or ImageFaker._faker.sentence(),
        )
