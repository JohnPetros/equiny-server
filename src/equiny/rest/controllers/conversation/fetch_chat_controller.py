from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases.get_chat_use_case import GetChatUseCase
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.shared.id_schema import IdSchema
from equiny.core.shared.domain.structures.id import Id


class FetchChatController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/',
            status_code=HTTPStatus.OK,
            response_model=ChatDto,
        )
        def _(
            chat_id: IdSchema,
            sender_id: Id = Depends(ProfilingPipe.get_owner_id),
            repository: ChatsRepository = Depends(DatabasePipe.get_chats_repository),
        ) -> ChatDto:
            use_case = GetChatUseCase(repository)
            return use_case.execute(chat_id=chat_id, sender_id=sender_id.value)
