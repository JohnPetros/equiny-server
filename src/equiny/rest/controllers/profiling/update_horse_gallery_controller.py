from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.structures.dtos import GalleryDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.update_horse_gallery_use_case import (
    UpdateHorseGalleryUseCase,
)
from equiny.core.shared.domain.structures import Id
from equiny.core.shared.interfaces.broker import Broker
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.pipes.pubsub_pipe import PubSubPipe
from equiny.validation.profiling.gallery_schema import GallerySchema


class UpdateHorseGalleryController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.put(
            '/{horse_id}/gallery',
            status_code=HTTPStatus.OK,
            response_model=GallerySchema,
        )
        def _(
            body: GallerySchema,
            horse_id: str,
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            horses_repository: HorsesRepository = Depends(
                DatabasePipe.get_horses_repository
            ),
            broker: Broker = Depends(PubSubPipe.get_broker),
        ) -> GalleryDto:
            use_case = UpdateHorseGalleryUseCase(horses_repository, broker)
            return use_case.execute(owner_id.value, horse_id, body.to_dto())
