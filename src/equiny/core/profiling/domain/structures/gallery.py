from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.profiling.domain.structures.dtos.gallery_dto import GalleryDto
from equiny.core.profiling.domain.structures.image import Image


@structure
class Gallery(Structure):
    images: list[Image]

    @classmethod
    def create(cls, dto: GalleryDto) -> 'Gallery':
        return cls(
            images=[Image.create(image_dto) for image_dto in dto.images],
        )

    def get_removed_images(self, old_gallery: 'Gallery') -> list[Image]:
        new_keys = {image.key.value for image in self.images}
        return [
            image for image in old_gallery.images if image.key.value not in new_keys
        ]

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
