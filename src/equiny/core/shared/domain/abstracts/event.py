from abc import ABC
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Event(ABC):
    name: str
    _payload: Any | None = None

    @property
    def payload(self) -> dict[str, Any]:
        if self._payload is None:
            return {}
        return asdict(self._payload)
