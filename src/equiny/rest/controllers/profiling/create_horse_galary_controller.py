from http import HTTPStatus
from pydantic import BaseModel, Field, model_validator
from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.structures.dtos.galary_dto import GalaryDto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.create_horse_galary_use_case import (
    CreateHorseGalaryUseCase,
)
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe


class _ImageSchema(BaseModel):
    key: str
    name: str


class BodySchema(BaseModel):
    images: list[_ImageSchema] = Field(min_length=1, max_length=9)

    @model_validator(mode='after')
    def check_unique_keys(self) -> 'BodySchema':
        keys = [image.key for image in self.images]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate keys are not allowed')
        return self

    def to_dtos(self) -> list[ImageDto]:
        return [
            ImageDto(key=image.key, name=image.name) for image in self.images
        ]


class CreateHorseGalaryController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/{horse_id}/galery',
            status_code=HTTPStatus.CREATED,
            response_model=GalaryDto,
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            horse_id: str,
            body: BodySchema,
            repository: HorsesRepository = Depends(
                DatabasePipe.get_horses_repository
            ),
        ) -> GalaryDto:
            use_case = CreateHorseGalaryUseCase(repository)
            return use_case.execute(horse_id, body.to_dtos())
