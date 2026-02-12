from os import getenv
from typing import NamedTuple


class Env(NamedTuple):
    HOST: str = str(getenv('HOST', '127.0.0.1'))
    PORT: int = int(getenv('PORT', 8080))
    DATABASE_URL: str = str(
        getenv('DATABASE_URL', 'postgresql://equiny:equiny@localhost:5432/equiny')
    )
    INNGEST_SIGNING_KEY: str = str(getenv('INNGEST_SIGNING_KEY', ''))
    JWT_SECRET: str = str(getenv('JWT_SECRET', ''))
