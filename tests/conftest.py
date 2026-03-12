import os
from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

os.environ.setdefault('INNGEST_SIGNING_KEY', 'test-signing-key')
os.environ.setdefault('JWT_SECRET', 'test-jwt-secret')
os.environ.setdefault('SUPABASE_URL', 'https://example.supabase.co')
os.environ.setdefault('SUPABASE_KEY', 'test-supabase-key')
os.environ.setdefault('SUPABASE_STORAGE_BUCKET', 'test-bucket')
os.environ.setdefault('ONESIGNAL_APP_ID', 'test-onesignal-app-id')
os.environ.setdefault('ONESIGNAL_API_KEY', 'test-onesignal-api-key')
os.environ.setdefault('EMAIL_VERIFICATION_SECRET', 'test-email-verification-secret')
os.environ.setdefault('EQUINY_SERVER_URL', 'http://localhost:8080')
os.environ.setdefault('RESEND_API_KEY', 'test-resend-api-key')
os.environ.setdefault('RESEND_SENDER_EMAIL', 'noreply@example.com')

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
