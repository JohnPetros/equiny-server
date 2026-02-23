# from fastapi import APIRouter, Depends, WebSocket
# from starlette.websockets import WebSocketDisconnect

# from equiny.constants import CHANNEL_KEYS
# from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
# from equiny.core.shared.domain.structures.id import Id
# from equiny.database.sqlalchemy.repositories.conversation import (
#     SqlalchemyChatsRepository,
#     SqlalchemyMessagesRepository,
# )
# from equiny.pipes.auth_pipe import AuthPipe
# from equiny.websocket.rooms.ws import Ws
# from equiny.core.conversation.use_cases import SendMessageUseCase
# from equiny.core.shared.domain.errors.app_error import AppError
# from equiny.validation.shared import IdSchema, Schema
# from equiny.database.sqlalchemy import Sqlalchemy
# from equiny.pipes.database_pipe import DatabasePipe
# from equiny.pipes.conversation_pipe import ConversationPipe


# class JsonSchema(Schema):
#     content: str


# class ChatRoom:
#     @staticmethod
#     def handle(router: APIRouter) -> None:
#         ws = Ws()

#         @router.websocket(
#             '/{chat_id}/{owner_id}',
#         )
#         async def _(
#             socket: WebSocket,
#             chat_id: IdSchema,
#             _: dict[str, str] = Depends(AuthPipe.verify_jwt_from_query),
#             owner_id: Id = Depends(ConversationPipe.verify_chat_participant),
#             sqlalchemy: Sqlalchemy = Depends(DatabasePipe.get_sqlalchemy),
#         ) -> None:
#             channel_key = f'{CHANNEL_KEYS.CHATS}:{chat_id}'
#             await ws.connect(channel_key, socket)
#             try:
#                 while True:
#                     json = await socket.receive_json()
#                     data = JsonSchema.model_validate(json)
#                     is_recipient_connected = ws.count_sockets(channel_key) > 1
#                     with sqlalchemy.session() as sqlalchemy_session:
#                         chats_repository = SqlalchemyChatsRepository(sqlalchemy_session)
#                         messages_repository = SqlalchemyMessagesRepository(
#                             sqlalchemy_session
#                         )
#                         use_case = SendMessageUseCase(
#                             chats_repository=chats_repository,
#                             messages_repository=messages_repository,
#                         )
#                         message_dto = use_case.execute(
#                             MessageDto(
#                                 content=data.content,
#                                 sender_id=owner_id.value,
#                                 attachments=[],
#                             ),
#                             chat_id,
#                             is_recipient_connected=is_recipient_connected,
#                         )
#                         await ws.broadcast(channel_key, message_dto)
#             except (WebSocketDisconnect, AppError, RuntimeError) as error:
#                 print('Error', error)
#                 ws.disconnect(channel_key, socket)
