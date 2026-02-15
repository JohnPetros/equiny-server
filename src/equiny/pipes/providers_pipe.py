from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.providers.hash import PwdlibHashProvider
from equiny.providers.jwt import JoseJwtProvider
from equiny.providers.storage.supabase import SupabaseFileStorageProvider


class ProvidersPipe:
    @staticmethod
    def get_hash_provider() -> HashProvider:
        return PwdlibHashProvider()

    @staticmethod
    def get_jwt_provider() -> JoseJwtProvider:
        return JoseJwtProvider()

    @staticmethod
    def get_file_storage_provider() -> FileStorageProvider:
        return SupabaseFileStorageProvider()
