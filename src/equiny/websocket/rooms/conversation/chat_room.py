from dataclasses import asdict
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.database.sqlalchemy.repositories.conversation import (
    SqlalchemyChatsRepository,
    SqlalchemyMessagesRepository,
)
from equiny.websocket.rooms.ws import Ws
from equiny.core.conversation.use_cases import SendMessageUseCase
from equiny.core.shared.domain.errors.app_error import AppError
from equiny.validation.shared import IdSchema, Schema
from equiny.database.sqlalchemy import Sqlalchemy


class JsonSchema(Schema):
    content: str
    sender_id: str

    def to_message_dto(self) -> MessageDto:
        return MessageDto(
            content=self.content,
            sender_id=self.sender_id,
            attachments=[],
        )


class ChatRoom:
    @staticmethod
    def handle(router: APIRouter) -> None:
        ws = Ws()

        @router.websocket(
            '/{chat_id}',
        )
        async def _(
            socket: WebSocket,
            chat_id: IdSchema,
        ) -> None:
            await ws.connect(socket)
            try:
                while True:
                    json = await socket.receive_json()
                    data = JsonSchema.model_validate(json)
                    with Sqlalchemy.session() as sqlalchemy:
                        chats_repository = SqlalchemyChatsRepository(sqlalchemy)
                        messages_repository = SqlalchemyMessagesRepository(sqlalchemy)
                        use_case = SendMessageUseCase(
                            chats_repository, messages_repository
                        )
                        response = use_case.execute(data.to_message_dto(), chat_id)
                        print('Response', asdict(response))
                        await ws.broadcast(response)
            except (WebSocketDisconnect, AppError, RuntimeError) as error:
                print('Error', error)
                ws.disconnect(socket)
