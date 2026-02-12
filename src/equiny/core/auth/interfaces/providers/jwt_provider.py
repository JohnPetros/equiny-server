from typing import Protocol


class JwtProvider(Protocol):
    def encode(self, subject: str) -> str: ...

    def decode(self, token: str) -> dict[str, str]: ...
