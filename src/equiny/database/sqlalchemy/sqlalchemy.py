from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from equiny.constants import ENV

DATABASE_URL = (
    ENV.DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
    if ENV.DATABASE_URL.startswith('postgresql://')
    else ENV.DATABASE_URL
)

engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False}
    if DATABASE_URL.startswith('sqlite')
    else {},
)

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


class Sqlalchemy:
    @staticmethod
    def get_session() -> Session:
        return SessionLocal()

    @staticmethod
    def get_request_session(request: Request) -> Session:
        return request.state.sqlalchemy_session
