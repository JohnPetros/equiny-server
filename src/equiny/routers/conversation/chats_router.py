from fastapi import APIRouter

from equiny.rest.controllers.conversation import (
    CreateChatController,
    FetchChatController,
    ListChatsController,
    ListMessagesController,
)
from equiny.websocket.rooms.conversation import ChatRoom


class ChatsRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/chats')

        CreateChatController.handle(router)
        FetchChatController.handle(router)
        ListChatsController.handle(router)
        ListMessagesController.handle(router)
        ChatRoom.handle(router)

        return router
