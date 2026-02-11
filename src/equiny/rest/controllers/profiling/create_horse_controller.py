from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.validation.profiling import HorseSchema
from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.use_cases import CreateHorseUseCase
from equiny.database.sqlalchemy.repositories import SqlalchemyHorsesRepository


class CreateHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/',
            status_code=HTTPStatus.CREATED,
            response_model=HorseDto,
        )
        def _(
            body: HorseSchema,
            sqlalchemy: Annotated[Session, Depends(Sqlalchemy.get_request_session)],
        ) -> HorseDto:
            repository = SqlalchemyHorsesRepository(sqlalchemy)
            use_case = CreateHorseUseCase(repository)
            return use_case.execute(body.to_dto())
