import pytest

from equiny.providers.jwt import JoseJwtProvider


@pytest.fixture
def auth_headers() -> dict[str, str]:
    token = JoseJwtProvider().encode('test-user')
    return {'Authorization': f'Bearer {token}'}
