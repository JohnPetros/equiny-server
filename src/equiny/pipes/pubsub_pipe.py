from fastapi import Request, WebSocket

from equiny.core.shared.interfaces.broker import Broker
from equiny.pubsub.inngest.inngest_broker import InngestBroker
from equiny.pubsub.redis.brokers.redis_matching_broker import RedisMatchingBroker


class PubSubPipe:
    @staticmethod
    def get_broker_from_request(request: Request) -> Broker:
        inngest = request.state.inngest_client
        return InngestBroker(inngest)

    @staticmethod
    def get_redis_pubsub_from_websocket(websocket: WebSocket) -> Broker:
        return websocket.app.state.redis_pubsub

    @staticmethod
    def get_redis_matching_broker(request: Request) -> Broker:
        redis_pubsub = request.app.state.redis_pubsub
        return RedisMatchingBroker(redis_pubsub)
