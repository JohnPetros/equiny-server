from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.profiling.domain.structures.dtos.gallery_dto import GalleryDto
from equiny.core.profiling.domain.structures.image import Image
from equiny.core.profiling.domain.structures.dtos import ImageDto


@structure
class Gallery(Structure):
    images: list[Image]

    @classmethod
    def create(cls, images_dtos: list[ImageDto]) -> 'Gallery':
        return cls(
            images=[Image.create(image_dto) for image_dto in images_dtos],
        )

    def insert_at_position(self, image: Image, position: int) -> 'Gallery':
        return type(self)(
            images=[
                *self.images[:position],
                image,
                *self.images[position:],
            ],
        )

    @property
    def dto(self) -> GalleryDto:
        return GalleryDto(
            images=[image.dto for image in self.images],
        )
