from typing import Protocol

from equiny.core.shared.domain.structures.text import Text


class GoogleAuthProvider(Protocol):
    def authenticate(self, id_token: Text) -> tuple[str, str]: ...
