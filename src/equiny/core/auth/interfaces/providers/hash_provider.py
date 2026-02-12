from typing import Protocol


class HashProvider(Protocol):
    def generate(self, password: str) -> str: ...

    def verify(self, password: str, hashed_password: str) -> bool: ...
