from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.domain.structures.gallery import Gallery
from equiny.core.profiling.domain.structures.breed import BreedValue
from equiny.core.profiling.domain.structures.sex import SexValue
from equiny.database.sqlalchemy.mappers.profiling.horses_mapper import HorsesMapper
from equiny.database.sqlalchemy.mappers.profiling.horse_images_mapper import (
    HorseImagesMapper,
)
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)
from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel
from equiny.database.sqlalchemy.models.profiling.horse_image_model import (
    HorseImageModel,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.domain.structures.image import Image


class SqlalchemyHorsesRepository(SqlalchemyRepository, HorsesRepository):
    def add(self, horse: Horse, owner_id: Id) -> None:
        horse_model = HorsesMapper.to_model(horse)
        horse_model.owner_id = owner_id.value
        self.sqlalchemy.add(horse_model)

    def add_many(self, horses: list[Horse], owner_id: Id) -> None:
        horse_models = [HorsesMapper.to_model(horse) for horse in horses]
        for horse_model in horse_models:
            horse_model.owner_id = owner_id.value
        self.sqlalchemy.add_all(horse_models)

    def find_by_id(self, horse_id: Id) -> Horse | None:
        horse_model = (
            self.sqlalchemy.query(HorseModel)
            .filter(HorseModel.id == horse_id.value)
            .first()
        )
        if horse_model is None:
            return None
        return HorsesMapper.to_entity(horse_model)

    def find_by_id_and_owner_id(self, horse_id: Id, owner_id: Id) -> Horse | None:
        horse_model = (
            self.sqlalchemy.query(HorseModel)
            .filter(HorseModel.id == horse_id.value)
            .filter(HorseModel.owner_id == owner_id.value)
            .first()
        )
        if horse_model is None:
            return None
        return HorsesMapper.to_entity(horse_model)

    def add_many_images(self, horse_id: Id, images: list[Image]) -> None:
        image_models = HorseImagesMapper.to_models(images, horse_id)
        self.sqlalchemy.add_all(image_models)

    def find_gallery_by_horse_id(self, horse_id: Id) -> Gallery | None:
        image_models = (
            self.sqlalchemy.query(HorseImageModel)
            .filter(HorseImageModel.horse_id == horse_id.value)
            .order_by(HorseImageModel.position)
            .all()
        )
        if not image_models:
            return None
        return HorseImagesMapper.to_gallery(image_models)

    def delete_many_images(self, horse_id: Id) -> None:
        self.sqlalchemy.query(HorseImageModel).filter(
            HorseImageModel.horse_id == horse_id.value
        ).delete()

    def replace(self, horse: Horse) -> None:
        horse_model = (
            self.sqlalchemy.query(HorseModel)
            .filter(HorseModel.id == horse.id.value)
            .first()
        )
        if horse_model is None:
            return

        horse_dto = horse.dto
        horse_model.name = horse_dto.name
        horse_model.birth_month = horse_dto.birth_month
        horse_model.birth_year = horse_dto.birth_year
        horse_model.height = horse_dto.height
        horse_model.breed = BreedValue(horse_dto.breed)
        horse_model.sex = SexValue(horse_dto.sex)
        horse_model.location_city = horse_dto.location.city
        horse_model.location_state = horse_dto.location.state
        horse_model.is_active = horse_dto.is_active
