from fastapi import APIRouter

from equiny.rest.controllers.conversation import (
    CreateChatController,
    FetchChatController,
    FetchChatsListController,
    FetchMessagesListController,
)
from equiny.websocket.rooms.conversation import ChatRoom


class ChatsRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/chats')

        CreateChatController.handle(router)
        FetchChatController.handle(router)
        FetchChatsListController.handle(router)
        FetchMessagesListController.handle(router)
        ChatRoom.handle(router)

        return router
