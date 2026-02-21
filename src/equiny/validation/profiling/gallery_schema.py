from pydantic import BaseModel, Field

from equiny.core.shared.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.domain.structures.dtos.gallery_dto import GalleryDto


class ImageSchema(BaseModel):
    key: str
    name: str


class GallerySchema(BaseModel):
    images: list[ImageSchema] = Field(min_length=1, max_length=9)

    def to_dto(self) -> GalleryDto:
        return GalleryDto(
            images=[ImageDto(key=image.key, name=image.name) for image in self.images]
        )
