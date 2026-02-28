from datetime import datetime

from sqlalchemy import case
from sqlalchemy.orm import aliased, selectinload

from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.domain.structures.gallery import Gallery
from equiny.core.profiling.domain.structures.breed import Breed, BreedValue
from equiny.core.profiling.domain.structures.sex import Sex, SexValue
from equiny.core.profiling.domain.structures.age_range import AgeRange
from equiny.core.profiling.domain.structures.location import Location
from equiny.core.shared.responses.pagination_response import PaginationResponse
from equiny.database.sqlalchemy.mappers.profiling.horses_mapper import HorsesMapper
from equiny.database.sqlalchemy.mappers.profiling.horse_matches_mapper import (
    HorseMatchesMapper,
)
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
from equiny.database.sqlalchemy.models.matching.swipe_model import SwipeModel
from equiny.database.sqlalchemy.models.matching.match_model import MatchModel
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.image import Image
from equiny.core.profiling.domain.structures.feed_horse import FeedHorse
from equiny.core.profiling.domain.structures.dtos.feed_horse_dto import FeedHorseDto


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

    def find_many_by_owner(self, owner_id: Id) -> list[Horse]:
        horse_models = (
            self.sqlalchemy.query(HorseModel)
            .filter(HorseModel.owner_id == owner_id.value)
            .all()
        )
        return [HorsesMapper.to_entity(horse_model) for horse_model in horse_models]

    def find_all_matches(self, horse_id: Id) -> list[HorseMatch]:
        paired_horse_id = case(
            (MatchModel.horse_a_id == horse_id.value, MatchModel.horse_b_id),
            else_=MatchModel.horse_a_id,
        )

        matches_rows = (
            self.sqlalchemy.query(HorseModel, MatchModel)
            .join(MatchModel, HorseModel.id == paired_horse_id)
            .filter(
                (MatchModel.horse_a_id == horse_id.value)
                | (MatchModel.horse_b_id == horse_id.value)
            )
            .order_by(MatchModel.created_at.desc())
            .all()
        )

        return [
            HorseMatchesMapper.to_structure(
                horse_model,
                match_model.created_at,
                match_model.has_horse_a_viewed
                if match_model.horse_a_id == horse_id.value
                else match_model.has_horse_b_viewed,
            )
            for horse_model, match_model in matches_rows
        ]

    def find_horse_matches_by_owner_id(self, owner_id: Id) -> list[HorseMatch]:
        horse_a = aliased(HorseModel)
        horse_b = aliased(HorseModel)
        paired_horse = aliased(HorseModel)

        paired_horse_id = case(
            (horse_a.owner_id == owner_id.value, horse_b.id),
            else_=horse_a.id,
        )

        is_viewed = case(
            (horse_a.owner_id == owner_id.value, MatchModel.has_horse_a_viewed),
            else_=MatchModel.has_horse_b_viewed,
        )

        matches_rows = (
            self.sqlalchemy.query(paired_horse, MatchModel.created_at, is_viewed)
            .select_from(MatchModel)
            .join(horse_a, horse_a.id == MatchModel.horse_a_id)
            .join(horse_b, horse_b.id == MatchModel.horse_b_id)
            .join(paired_horse, paired_horse.id == paired_horse_id)
            .options(
                selectinload(paired_horse.owner),
            )
            .filter(
                (horse_a.owner_id == owner_id.value)
                | (horse_b.owner_id == owner_id.value)
            )
            .order_by(MatchModel.created_at.desc())
            .all()
        )
        return [
            HorseMatchesMapper.to_structure(horse_model, created_at, viewed)
            for horse_model, created_at, viewed in matches_rows
        ]

    def find_horse_match_by_horses(
        self, from_horse_id: Id, to_horse_id: Id
    ) -> HorseMatch | None:
        match_model = (
            self.sqlalchemy.query(MatchModel)
            .filter(
                (
                    (MatchModel.horse_a_id == from_horse_id.value)
                    & (MatchModel.horse_b_id == to_horse_id.value)
                )
                | (
                    (MatchModel.horse_a_id == to_horse_id.value)
                    & (MatchModel.horse_b_id == from_horse_id.value)
                )
            )
            .first()
        )
        if match_model is None:
            return None

        owner_horse_model = (
            self.sqlalchemy.query(HorseModel)
            .filter(HorseModel.id == to_horse_id.value)
            .first()
        )
        if owner_horse_model is None:
            return None

        is_viewed = (
            match_model.has_horse_a_viewed
            if match_model.horse_a_id == from_horse_id.value
            else match_model.has_horse_b_viewed
        )

        return HorseMatchesMapper.to_structure(
            owner_horse_model,
            match_model.created_at,
            is_viewed,
        )

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
        horse_model.description = horse_dto.description
        horse_model.height = horse_dto.height
        horse_model.breed = BreedValue(horse_dto.breed)
        horse_model.sex = SexValue(horse_dto.sex)
        horse_model.location_city = horse_dto.location.city
        horse_model.location_state = horse_dto.location.state
        horse_model.is_active = horse_dto.is_active

    def replace_horse_match(
        self,
        from_horse_id: Id,
        to_horse_id: Id,
        horse_match: HorseMatch,
    ) -> None:
        horse_a_match_model = (
            self.sqlalchemy.query(MatchModel)
            .filter(MatchModel.horse_a_id == from_horse_id.value)
            .filter(MatchModel.horse_b_id == to_horse_id.value)
            .first()
        )
        if horse_a_match_model:
            horse_a_match_model.has_horse_a_viewed = horse_match.is_viewed.value
            return

        horse_b_match_model = (
            self.sqlalchemy.query(MatchModel)
            .filter(MatchModel.horse_b_id == from_horse_id.value)
            .filter(MatchModel.horse_a_id == to_horse_id.value)
            .first()
        )
        if horse_b_match_model:
            horse_b_match_model.has_horse_b_viewed = horse_match.is_viewed.value

    def find_many_feed_horses(
        self,
        horse_id: Id,
        sex: Sex,
        age_range: AgeRange,
        breeds: list[Breed],
        location: Location,
        cursor: Id | None = None,
        limit: int = 20,
    ) -> PaginationResponse[FeedHorse]:
        query = self.sqlalchemy.query(HorseModel).filter(HorseModel.is_active)

        query = query.filter(HorseModel.id != horse_id.value)

        query = query.filter(HorseModel.sex == SexValue(sex.dto))

        if breeds:
            breed_values = [BreedValue(breed.dto) for breed in breeds]
            query = query.filter(HorseModel.breed.in_(breed_values))

        query = query.filter(HorseModel.location_city == location.city.value)
        query = query.filter(HorseModel.location_state == location.state.value)

        current_year = datetime.now().year
        min_birth_year = current_year - age_range.max_age.value
        max_birth_year = current_year - age_range.min_age.value

        query = query.filter(HorseModel.birth_year >= min_birth_year)
        query = query.filter(HorseModel.birth_year <= max_birth_year)

        swipe_exists = (
            self.sqlalchemy.query(SwipeModel)
            .filter(
                (SwipeModel.from_horse_id == horse_id.value)
                & (SwipeModel.to_horse_id == HorseModel.id)
            )
            .exists()
        )
        query = query.filter(~swipe_exists)

        if cursor:
            query = query.filter(HorseModel.id < cursor.value)

        models = query.order_by(HorseModel.id.desc()).limit(limit + 1).all()

        has_more = len(models) > limit
        if has_more:
            models = models[:limit]

        horse_ids = [model.id for model in models]
        galleries_by_horse_id: dict[str, Gallery] = {}

        if horse_ids:
            image_models = (
                self.sqlalchemy.query(HorseImageModel)
                .filter(HorseImageModel.horse_id.in_(horse_ids))
                .order_by(HorseImageModel.position)
                .all()
            )

            images_by_horse_id: dict[str, list[Image]] = {}
            for image_model in image_models:
                image_entity = HorseImagesMapper.to_entity(image_model)
                images_by_horse_id.setdefault(image_model.horse_id, []).append(
                    image_entity
                )

            for horse_id_value, images in images_by_horse_id.items():
                galleries_by_horse_id[horse_id_value] = Gallery(images=images)

        feed_horses: list[FeedHorse] = []
        for model in models:
            horse = HorsesMapper.to_entity(model)
            gallery = galleries_by_horse_id.get(horse.id.value)
            if gallery is None:
                gallery = Gallery.create_empty()
            feed_horse_dto = FeedHorseDto(
                horse=horse.dto,
                gallery=gallery.dto,
            )
            feed_horses.append(FeedHorse.create(feed_horse_dto))

        next_cursor = feed_horses[-1].horse.id.value if has_more else None

        return PaginationResponse(
            items=feed_horses, next_cursor=next_cursor, has_more=has_more
        )
