from http import HTTPStatus
from fastapi import APIRouter, Depends, Query

from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.interfaces.messages_repository import MessagesRepository
from equiny.core.conversation.use_cases.list_messages_use_case import (
    ListMessagesUseCase,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.responses.pagination_response import PaginationResponse
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.validation.shared.id_schema import IdSchema


class ListMessagesController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{chat_id}/messages',
            status_code=HTTPStatus.OK,
            response_model=PaginationResponse[MessageDto],
        )
        def _(
            chat_id: IdSchema,
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            chats_repository: ChatsRepository = Depends(
                DatabasePipe.get_chats_repository
            ),
            messages_repository: MessagesRepository = Depends(
                DatabasePipe.get_messages_repository
            ),
            cursor: IdSchema | None = Query(default=None),
            limit: int = Query(default=20, ge=1, le=100),
        ) -> PaginationResponse[MessageDto]:
            use_case = ListMessagesUseCase(chats_repository, messages_repository)
            return use_case.execute(
                chat_id=chat_id,
                sender_id=owner_id.value,
                cursor=cursor,
                limit=limit,
            )
