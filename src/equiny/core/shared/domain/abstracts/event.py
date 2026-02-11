from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    name: str
