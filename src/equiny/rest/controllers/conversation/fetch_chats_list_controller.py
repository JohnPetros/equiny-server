from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases.list_chats_use_case import ListChatsUseCase
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.responses.list_response import ListResponse
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe


class FetchChatsListController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/list',
            status_code=HTTPStatus.OK,
            response_model=ListResponse[ChatDto],
        )
        def _(
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            repository: ChatsRepository = Depends(DatabasePipe.get_chats_repository),
        ) -> ListResponse[ChatDto]:
            use_case = ListChatsUseCase(repository)
            return ListResponse[ChatDto](items=use_case.execute(owner_id.value))
