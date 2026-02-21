from fastapi import APIRouter

from equiny.routers.conversation.chats_router import ChatsRouter


class ConversationRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/conversation', tags=['Conversation module'])

        router.include_router(ChatsRouter.register())

        return router
