from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases.get_chat_use_case import GetChatUseCase
from equiny.pipes.conversation_pipe import ConversationPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.shared.id_schema import IdSchema
from equiny.core.shared.domain.structures.id import Id


class FetchChatController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{chat_id}',
            status_code=HTTPStatus.OK,
            response_model=ChatDto,
        )
        def _(
            chat_id: IdSchema,
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            _: None = Depends(ConversationPipe.verify_chat_participant),
            repository: ChatsRepository = Depends(DatabasePipe.get_chats_repository),
        ) -> ChatDto:
            use_case = GetChatUseCase(repository)
            return use_case.execute(chat_id=chat_id, sender_id=owner_id.value)
