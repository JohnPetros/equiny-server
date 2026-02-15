from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.database.sqlalchemy.mappers.profiling.horses_mapper import HorsesMapper
from equiny.database.sqlalchemy.mappers.profiling.horse_images_mapper import (
    HorseImagesMapper,
)
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)
from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel
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

    def add_many_images(self, horse_id: Id, images: list[Image]) -> None:
        image_models = HorseImagesMapper.to_models(images, horse_id)
        self.sqlalchemy.add_all(image_models)
