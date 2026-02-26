from equiny.core.shared.interfaces.broker import Broker
from equiny.pubsub.redis import RedisPubSub


class RedisBroker(Broker):
    pubsub: RedisPubSub

    def __init__(self, pubsub: RedisPubSub) -> None:
        self.pubsub = pubsub
