from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.profiling.domain.structures.dtos.galary_dto import GalaryDto
from equiny.core.profiling.domain.structures.image import Image
from equiny.core.profiling.domain.structures.dtos import ImageDto


@structure
class Galery(Structure):
    images: list[Image]

    @classmethod
    def create(cls, images_dtos: list[ImageDto]) -> 'Galery':
        return cls(
            images=[Image.create(image_dto) for image_dto in images_dtos],
        )

    def insert_at_position(self, image: Image, position: int) -> 'Galery':
        return type(self)(
            images=[
                *self.images[:position],
                image,
                *self.images[position:],
            ],
        )

    @property
    def dto(self) -> GalaryDto:
        return GalaryDto(
            images=[image.dto for image in self.images],
        )
