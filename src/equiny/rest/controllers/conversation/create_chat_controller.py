from http import HTTPStatus
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases.create_chat_use_case import CreateChatUseCase
from equiny.core.shared.domain.structures.id import Id
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.shared.id_schema import IdSchema


class _BodySchema(BaseModel):
    recipient_id: IdSchema


class CreateChatController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/',
            status_code=HTTPStatus.CREATED,
            response_model=ChatDto,
        )
        def _(
            body: _BodySchema,
            sender_id: Id = Depends(ProfilingPipe.get_owner_id),
            repository: ChatsRepository = Depends(DatabasePipe.get_chats_repository),
        ) -> ChatDto:
            use_case = CreateChatUseCase(repository)
            return use_case.execute(body.recipient_id, sender_id.value)
