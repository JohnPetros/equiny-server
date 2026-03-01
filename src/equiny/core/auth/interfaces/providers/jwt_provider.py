from typing import Protocol

from equiny.core.auth.domain.structures.dtos.jwt_dto import JwtDto


class JwtProvider(Protocol):
    def encode(self, subject: str) -> JwtDto: ...

    def decode(self, token: str) -> dict[str, str]: ...
