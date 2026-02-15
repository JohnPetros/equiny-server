from http import HTTPStatus
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.structures.dtos import GalleryDto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.create_horse_gallery_use_case import (
    CreateHorseGalleryUseCase,
)
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.validation.profiling.galery_schema import ImageSchema


class BodySchema(BaseModel):
    images: list[ImageSchema] = Field(min_length=1, max_length=9)

    def to_dtos(self) -> list[ImageDto]:
        return [ImageDto(key=image.key, name=image.name) for image in self.images]


class CreateHorseGalleryController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/{horse_id}/gallery',
            status_code=HTTPStatus.CREATED,
            response_model=GalleryDto,
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            horse_id: str,
            body: BodySchema,
            repository: HorsesRepository = Depends(DatabasePipe.get_horses_repository),
        ) -> GalleryDto:
            use_case = CreateHorseGalleryUseCase(repository)
            return use_case.execute(horse_id, body.to_dtos())
