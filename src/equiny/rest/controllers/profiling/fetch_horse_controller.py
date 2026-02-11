from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.use_cases.get_horse_use_case import GetHorseUseCase
from equiny.database.sqlalchemy.repositories import SqlalchemyHorsesRepository


class FetchHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{horse_id}',
            status_code=HTTPStatus.OK,
            response_model=HorseDto,
        )
        def _(
            horse_id: str,
            sqlalchemy: Annotated[Session, Depends(Sqlalchemy.get_request_session)],
        ) -> HorseDto:
            repository = SqlalchemyHorsesRepository(sqlalchemy)
            use_case = GetHorseUseCase(repository)
            return use_case.execute(horse_id)
