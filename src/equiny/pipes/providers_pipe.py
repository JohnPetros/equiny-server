from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.providers.hash import PwdlibHashProvider
from equiny.providers.jwt import JoseJwtProvider


class ProvidersPipe:
    @staticmethod
    def get_hash_provider() -> HashProvider:
        return PwdlibHashProvider()

    @staticmethod
    def get_jwt_provider() -> JoseJwtProvider:
        return JoseJwtProvider()
