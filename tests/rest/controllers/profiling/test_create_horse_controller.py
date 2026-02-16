from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from equiny.core.profiling.use_cases.create_owner_use_case import CreateOwnerUseCase
from equiny.database.sqlalchemy.repositories.profiling.sqlalchemy_owners_repository import (
    SqlalchemyOwnersRepository,
)
from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.providers.jwt import JoseJwtProvider


class TestCreateHorseController:
    def _auth_headers(self, client: TestClient) -> dict[str, str]:
        account_email = f'create-horse-{uuid4().hex}@example.com'

        client.post(
            '/auth/sign-up',
            json={
                'owner_name': 'John Owner',
                'account_email': account_email,
                'account_password': 'plain-password',
            },
        )

        sign_in_response = client.post(
            '/auth/sign-in',
            json={
                'email': account_email,
                'password': 'plain-password',
            },
        )

        access_token = sign_in_response.json()['access_token']
        account_id = JoseJwtProvider().decode(access_token)['sub']

        sqlalchemy = Sqlalchemy.get_session()
        try:
            repository = SqlalchemyOwnersRepository(sqlalchemy)
            CreateOwnerUseCase(repository).execute(
                owner_name='John Owner',
                owner_email=account_email,
                account_id=account_id,
            )
            sqlalchemy.commit()
        finally:
            sqlalchemy.close()

        return {'Authorization': f'Bearer {access_token}'}

    def test_should_create_horse_and_return_payload(self, client: TestClient) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'Test Horse',
                'birth_month': 1,
                'birth_year': 2020,
                'height': 1.62,
                'breed': 'arabe',
                'sex': 'male',
                'location': {'city': 'Sao Paulo', 'state': 'SP'},
            },
            headers=self._auth_headers(client),
        )

        assert response.status_code == 201

        data = response.json()
        assert data['id']
        assert data['name'] == 'Test Horse'
        assert data['birth_month'] == 1
        assert data['birth_year'] == 2020
        assert data['height'] == 1.62
        assert data['breed'] == 'arabe'
        assert data['sex'] == 'male'
        assert data['location'] == {'city': 'Sao Paulo', 'state': 'SP'}

    @pytest.mark.parametrize('birth_month', [0, 13])
    def test_should_return_422_when_birth_month_is_invalid(
        self,
        client: TestClient,
        birth_month: int,
    ) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'Test Horse',
                'birth_month': birth_month,
                'birth_year': 2020,
                'height': 1.62,
                'breed': 'arabe',
                'sex': 'male',
                'location': {'city': 'Sao Paulo', 'state': 'SP'},
            },
            headers=self._auth_headers(client),
        )

        assert response.status_code == 422

    def test_should_return_422_when_birth_year_is_in_the_future(
        self, client: TestClient
    ) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'Test Horse',
                'birth_month': 1,
                'birth_year': datetime.now().year + 1,
                'height': 1.62,
                'breed': 'arabe',
                'sex': 'male',
                'location': {'city': 'Sao Paulo', 'state': 'SP'},
            },
            headers=self._auth_headers(client),
        )

        assert response.status_code == 422

    def test_should_return_422_when_breed_is_invalid(self, client: TestClient) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'Test Horse',
                'birth_month': 1,
                'birth_year': 2020,
                'height': 1.62,
                'breed': 'invalid breed',
                'sex': 'male',
                'location': {'city': 'Sao Paulo', 'state': 'SP'},
            },
            headers=self._auth_headers(client),
        )

        assert response.status_code == 422

    def test_should_return_422_when_name_is_too_short(self, client: TestClient) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'AB',
                'birth_month': 1,
                'birth_year': 2020,
                'height': 1.62,
                'breed': 'arabe',
                'sex': 'male',
                'location': {'city': 'Sao Paulo', 'state': 'SP'},
            },
            headers=self._auth_headers(client),
        )

        assert response.status_code == 422
