import pytest

from collections.abc import Generator
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from equiny.database.sqlalchemy.models.model import Model
from equiny.database.sqlalchemy.models.matching.match_model import MatchModel
from equiny.database.sqlalchemy.models.matching.swipe_model import SwipeModel
from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel
from equiny.database.sqlalchemy.models.profiling.horse_image_model import HorseImageModel
from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel
from equiny.database.sqlalchemy.models.auth.account_model import AccountModel


@pytest.fixture(scope='session')
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer('postgres:16-alpine') as postgres:
        yield postgres


@pytest.fixture(scope='session')
def engine(postgres_container: PostgresContainer) -> Generator[Engine, None, None]:
    url = postgres_container.get_connection_url()
    url = url.replace('postgresql://', 'postgresql+psycopg2://')

    engine = create_engine(url, future=True)

    Model.metadata.create_all(bind=engine)

    yield engine
    engine.dispose()


@pytest.fixture
def sqlalchemy_session(engine: Engine) -> Generator[Session, None, None]:
    session_local = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    db = session_local()
    try:
        yield db
    finally:
        db.close()
