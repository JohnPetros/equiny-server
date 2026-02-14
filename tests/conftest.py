import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from unittest.mock import Mock
from uuid import uuid4

from equiny.app import FastAPIApp
from equiny.constants import ENV
from equiny.database.sqlalchemy.models.model import Model
from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.providers.jwt import JoseJwtProvider
from equiny.pubsub.inngest.inngest_pubsub import InngestPubSub

TEST_DATABASE_URL = (
    ENV.DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
    if ENV.DATABASE_URL.startswith('postgresql://')
    else ENV.DATABASE_URL
)


@pytest.fixture(scope='session')
def override_sqlalchemy_session_for_tests():
    if not TEST_DATABASE_URL.startswith('postgresql'):
        raise RuntimeError('Tests require a PostgreSQL DATABASE_URL.')

    schema_name = f'equiny_test_{uuid4().hex}'
    engine = create_engine(TEST_DATABASE_URL)
    schema_engine = engine.execution_options(schema_translate_map={None: schema_name})
    session_local = sessionmaker(
        bind=schema_engine, autoflush=False, autocommit=False, class_=Session
    )

    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        schema_connection = connection.execution_options(
            schema_translate_map={None: schema_name}
        )
        Model.metadata.create_all(bind=schema_connection)

    original_get_session = Sqlalchemy.get_session
    Sqlalchemy.get_session = staticmethod(lambda: session_local())

    try:
        yield
    finally:
        Sqlalchemy.get_session = original_get_session

        with engine.begin() as connection:
            schema_connection = connection.execution_options(
                schema_translate_map={None: schema_name}
            )
            Model.metadata.drop_all(bind=schema_connection)
            # connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))

        engine.dispose()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    token = JoseJwtProvider().encode('test-user')
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def client(mocker: MockerFixture) -> TestClient:
    mocker.patch.object(InngestPubSub, 'register', return_value=Mock())
    app = FastAPIApp.register()
    return TestClient(app)
