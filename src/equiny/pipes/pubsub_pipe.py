from fastapi import Depends, Request
from inngest import Inngest

from equiny.core.shared.interfaces.broker import Broker
from equiny.pubsub.inngest.inngest_broker import InngestBroker


def get_inngest_client(request: Request) -> Broker:
    return request.state.inngest_client


class PubSubPipe:
    @staticmethod
    def get_broker(
        inngest: Inngest = Depends(get_inngest_client),
    ) -> Broker:
        return InngestBroker(inngest)
