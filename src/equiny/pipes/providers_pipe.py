from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.auth.interfaces.providers.google_auth_provider import (
    GoogleAuthProvider,
)
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.notification.interfaces.email_sender_provider import (
    EmailProvider,
)
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.providers.auth.google import GoogleOauthProvider
from equiny.providers.auth.itsdangerous import ItsdangerousEmailVerificationProvider
from equiny.providers.hash import PwdlibHashProvider
from equiny.providers.jwt import JoseJwtProvider
from equiny.providers.email.resend import ResendEmailProvider
from equiny.providers.storage.supabase import SupabaseFileStorageProvider
from equiny.providers.cache.redis import RedisCacheProvider


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

    @staticmethod
    def get_cache_provider() -> CacheProvider:
        return RedisCacheProvider()

    @staticmethod
    def get_email_verification_provider() -> EmailVerificationProvider:
        return ItsdangerousEmailVerificationProvider()

    @staticmethod
    def get_google_auth_provider() -> GoogleAuthProvider:
        return GoogleOauthProvider()

    @staticmethod
    def get_email_provider() -> EmailProvider:
        return ResendEmailProvider()
