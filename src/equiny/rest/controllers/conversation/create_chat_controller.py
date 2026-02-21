from typing import Annotated

from http import HTTPStatus
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases.create_chat_use_case import CreateChatUseCase
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.matching_pipe import MatchingPipe
from equiny.validation.shared.id_schema import IdSchema

repository = Annotated[ChatsRepository, Depends(DatabasePipe.get_chats_repository)]


class BodySchema(BaseModel):
    recipient_id: IdSchema
    sender_id: IdSchema
    recipient_horse_id: IdSchema
    sender_horse_id: IdSchema


class CreateChatController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/',
            status_code=HTTPStatus.CREATED,
            response_model=ChatDto,
            dependencies=[Depends(MatchingPipe.verify_match)],
        )
        def _(
            body: BodySchema,
            repository: repository,
        ) -> ChatDto:
            use_case = CreateChatUseCase(repository)
            return use_case.execute(body.recipient_id, body.sender_id)
