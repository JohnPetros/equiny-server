from equiny.core.profiling.domain.structures.image import Image
from equiny.core.profiling.domain.structures.gallery import Gallery
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.database.sqlalchemy.models.profiling.horse_image_model import (
    HorseImageModel,
)
from equiny.core.shared.domain.structures.id import Id


class HorseImagesMapper:
    @staticmethod
    def to_model(image: Image, horse_id: Id, position: int) -> HorseImageModel:
        return HorseImageModel(
            id=Id.create().value,
            horse_id=horse_id.value,
            key=image.key.value,
            name=image.name.value,
            position=position,
        )

    @staticmethod
    def to_models(
        images: list[Image],
        horse_id: Id,
    ) -> list[HorseImageModel]:
        return [
            HorseImagesMapper.to_model(image, horse_id, position)
            for position, image in enumerate(images)
        ]

    @staticmethod
    def to_entity(model: HorseImageModel) -> Image:
        return Image.create(
            ImageDto(
                key=model.key,
                name=model.name,
            )
        )

    @staticmethod
    def to_gallery(models: list[HorseImageModel]) -> Gallery:
        sorted_models = sorted(models, key=lambda m: m.position)
        images = [HorseImagesMapper.to_entity(model) for model in sorted_models]
        return Gallery(images=images)
