from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from unittest.mock import Mock
from sqlalchemy.orm import Session

from equiny.app import FastAPIApp
from equiny.pubsub.inngest.inngest_pubsub import InngestPubSub
from equiny.pipes.database_pipe import get_sqlalchemy_session_from_request


@pytest.fixture
def client(mocker: MockerFixture, sqlalchemy_session: Session) -> TestClient:
    mocker.patch.object(InngestPubSub, 'register', return_value=Mock())

    def override_get_sqlalchemy_session() -> Generator[Session]:
        try:
            yield sqlalchemy_session
        finally:
            sqlalchemy_session.commit()

    app = FastAPIApp.register()
    app.dependency_overrides[get_sqlalchemy_session_from_request] = (
        override_get_sqlalchemy_session
    )
    return TestClient(app)


pytest_plugins = [
    'fixtures.auth_fixtures',
    'fixtures.database_fixtures',
]
