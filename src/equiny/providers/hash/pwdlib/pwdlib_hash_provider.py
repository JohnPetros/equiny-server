from pwdlib import PasswordHash
from equiny.core.auth.interfaces.providers import HashProvider


class PwdlibHashProvider(HashProvider):
    _pwdlib = PasswordHash.recommended()

    def generate(self, password: str) -> str:
        return self._pwdlib.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        return self._pwdlib.verify(password, hashed_password)
