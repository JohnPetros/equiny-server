from fastapi import APIRouter

from equiny.rest.controllers.profiling import (
    FetchOwnerController,
    FetchOwnerHorsesController,
    FetchOwnerPresenceController,
    UpdateOwnerController,
)
from equiny.websocket.rooms.profiling import OwnersPresenceRoom


class OwnersRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/owners')

        FetchOwnerController.handle(router)
        FetchOwnerHorsesController.handle(router)
        FetchOwnerPresenceController.handle(router)
        UpdateOwnerController.handle(router)
        OwnersPresenceRoom.handle(router)

        return router
