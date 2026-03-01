from fastapi import Request, WebSocket

from equiny.core.shared.interfaces.broker import Broker
from equiny.pubsub.inngest.inngest_broker import InngestBroker


class PubSubPipe:
    @staticmethod
    def get_broker_from_request(request: Request) -> Broker:
        inngest = request.state.inngest_client
        return InngestBroker(inngest)

    @staticmethod
    def get_redis_pubsub_from_websocket(websocket: WebSocket) -> Broker:
        return websocket.app.state.redis_pubsub
