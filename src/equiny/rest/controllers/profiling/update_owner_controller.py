from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.profiling.domain.structures.dtos import ImageDto
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.use_cases import UpdateOwnerUseCase
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.profiling import OwnerSchema
from equiny.pipes.pubsub_pipe import PubSubPipe
from equiny.core.shared.interfaces.broker import Broker
from equiny.validation.profiling.gallery_schema import ImageSchema
from equiny.validation.shared import EmailSchema, NameSchema


class BodySchema(OwnerSchema):
    name: NameSchema
    email: EmailSchema
    bio: str | None = None
    phone: str | None = None
    avatar: ImageSchema | None = None
    has_completed_onboarding: bool
    account_id: str


class UpdateOwnerController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.put(
            '/me',
            status_code=HTTPStatus.OK,
            response_model=OwnerDto,
        )
        def _(
            body: BodySchema,
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            repository: OwnersRepository = Depends(DatabasePipe.get_owners_repository),
            broker: Broker = Depends(PubSubPipe.get_broker),
        ) -> OwnerDto:
            use_case = UpdateOwnerUseCase(repository, broker)
            return use_case.execute(
                owner_id.value,
                OwnerDto(
                    bio=body.bio,
                    phone=None if body.phone == '' else body.phone,
                    avatar=ImageDto(key=body.avatar.key, name=body.avatar.name)
                    if body.avatar is not None
                    else None,
                    name=body.name,
                    email=body.email,
                    account_id=body.account_id,
                    has_completed_onboarding=body.has_completed_onboarding,
                ),
            )
