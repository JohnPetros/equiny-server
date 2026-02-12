from typing import Protocol

from equiny.core.shared.domain.abstracts import Event


class Broker(Protocol):
    def publish(self, event: Event) -> None: ...
