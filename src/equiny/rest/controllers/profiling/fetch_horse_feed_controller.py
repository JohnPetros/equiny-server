from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from equiny.core.profiling.domain.structures.dtos.feed_horse_dto import FeedHorseDto
from equiny.core.profiling.domain.structures.dtos.age_range_dto import AgeRangeDto
from equiny.core.profiling.interfaces.repositories.horsers_repository import (
    HorsesRepository,
)
from equiny.core.profiling.use_cases.get_horse_feed_use_case import (
    GetHorseFeedUseCase,
)
from equiny.core.profiling.domain.structures.breed import BreedValue
from equiny.core.profiling.domain.structures.sex import SexValue
from equiny.core.shared.responses.pagination_response import PaginationResponse
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes import DatabasePipe
from equiny.validation.shared import IdSchema


repository = Annotated[HorsesRepository, Depends(DatabasePipe.get_horses_repository)]


class FetchHorseFeedController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{horse_id}/feed',
            status_code=HTTPStatus.OK,
            response_model=PaginationResponse[FeedHorseDto],
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            horse_id: IdSchema,
            repository: repository,
            sex: SexValue,
            max_distance_in_km: int = Query(default=50, gt=0),
            breeds: list[BreedValue] = Query(default=[]),
            min_age: int = Query(default=0, ge=0, le=30),
            max_age: int = Query(default=30, ge=0, le=30),
            cursor: IdSchema | None = Query(default=None),
            limit: int = Query(default=20, ge=1, le=100),
        ) -> PaginationResponse[FeedHorseDto]:
            use_case = GetHorseFeedUseCase(repository)
            age_range_dto = AgeRangeDto(min_age=min_age, max_age=max_age)
            return use_case.execute(
                horse_id=horse_id,
                sex=sex.value,
                breeds=[breed.value for breed in breeds],
                age_range_dto=age_range_dto,
                max_distance_in_km=max_distance_in_km,
                cursor=cursor,
                limit=limit,
            )
