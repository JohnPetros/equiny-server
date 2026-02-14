from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(BaseSettings):
    HOST: str = '127.0.0.1'
    PORT: int = 8080
    DATABASE_URL: str = 'postgresql://equiny:equiny@localhost:5432/equiny'
    INNGEST_SIGNING_KEY: str
    JWT_SECRET: str

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
    )
