from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from equiny.core.profiling.domain.structures.dtos.feed_horse_dto import FeedHorseDto
from equiny.core.profiling.domain.structures.dtos.age_range_dto import AgeRangeDto
from equiny.core.profiling.domain.structures.dtos.location_dto import LocationDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.get_horse_feed_use_case import (
    GetHorseFeedUseCase,
)
from equiny.core.profiling.domain.structures.breed import BreedValue
from equiny.core.profiling.domain.structures.sex import SexValue
from equiny.core.shared.responses.pagination_response import PaginationResponse
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.validation.shared import IdSchema


class QuerySchema(BaseModel):
    sex: SexValue
    breeds: list[BreedValue] = Query(default=[])
    min_age: int = Query(default=0, ge=0, le=30)
    max_age: int = Query(default=30, ge=0, le=30)
    city: str
    state: str
    cursor: IdSchema | None = None
    limit: int = Query(default=20, ge=1, le=100)

    def to_age_range_dto(self) -> AgeRangeDto:
        return AgeRangeDto(min_age=self.min_age, max_age=self.max_age)

    def to_location_dto(self) -> LocationDto:
        return LocationDto(city=self.city, state=self.state)


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
            query: Annotated[QuerySchema, Depends()],
            repository: repository,
        ) -> PaginationResponse[FeedHorseDto]:
            use_case = GetHorseFeedUseCase(repository)
            print('FetchHorseFeedController.handle: query', query)
            return use_case.execute(
                horse_id=horse_id,
                sex=query.sex.value,
                breeds=[breed.value for breed in query.breeds],
                age_range_dto=query.to_age_range_dto(),
                location_dto=query.to_location_dto(),
                cursor=query.cursor,
                limit=query.limit,
            )
