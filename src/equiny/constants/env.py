from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(BaseSettings):
    HOST: str = '127.0.0.1'
    PORT: int = 8080
    DATABASE_URL: str = 'postgresql://equiny:equiny@localhost:5432/equiny'
    REDIS_URL: str = 'redis://localhost:6379/0'
    INNGEST_SIGNING_KEY: str
    JWT_SECRET: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_STORAGE_BUCKET: str
    ONESIGNAL_APP_ID: str
    ONESIGNAL_API_KEY: str
    EMAIL_VERIFICATION_SECRET: str
    EQUINY_SERVER_URL: str
    RESEND_API_KEY: str
    RESEND_SENDER_EMAIL: str
    GOOGLE_OAUTH_CLIENT_ID: str

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
    )
