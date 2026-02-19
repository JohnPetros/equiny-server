from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.domain.entities.dtos.owner_dto import OwnerDto
from equiny.database.sqlalchemy.repositories.profiling.sqlalchemy_owners_repository import (
    SqlalchemyOwnersRepository,
)
from equiny.database.sqlalchemy.repositories.auth.sqlalchemy_accounts_repository import (
    SqlalchemyAccountsRepository,
)
from equiny.providers.jwt import JoseJwtProvider


class TestCreateHorseController:
    def _auth_headers(self, sqlalchemy_session: Session) -> dict[str, str]:
        account_email = f'create-horse-{uuid4().hex}@example.com'

        password_hash = PasswordHash.recommended().hash('plain-password')

        accounts_repo = SqlalchemyAccountsRepository(sqlalchemy_session)
        account = Account.create(
            AccountDto(
                email=account_email, password=password_hash
            )
        )
        accounts_repo.add(account)
        sqlalchemy_session.flush()

        owners_repo = SqlalchemyOwnersRepository(sqlalchemy_session)
        owner = Owner.create(
            OwnerDto(
                name='John Owner',
                email=account_email,
                account_id=account.id.value,
                has_completed_onboarding=False,
            )
        )
        owners_repo.add(owner)
        sqlalchemy_session.commit()

        access_token = JoseJwtProvider().encode(account.id.value)

        return {'Authorization': f'Bearer {access_token}'}

    def test_should_create_horse_and_return_payload(
        self, client: TestClient, sqlalchemy_session: Session
    ) -> None:
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
            headers=self._auth_headers(sqlalchemy_session),
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
        sqlalchemy_session: Session,
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
            headers=self._auth_headers(sqlalchemy_session),
        )

        assert response.status_code == 422

    def test_should_return_422_when_birth_year_is_in_the_future(
        self, client: TestClient, sqlalchemy_session: Session
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
            headers=self._auth_headers(sqlalchemy_session),
        )

        assert response.status_code == 422

    def test_should_return_422_when_breed_is_invalid(
        self, client: TestClient, sqlalchemy_session: Session
    ) -> None:
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
            headers=self._auth_headers(sqlalchemy_session),
        )

        assert response.status_code == 422

    def test_should_return_422_when_name_is_too_short(
        self, client: TestClient, sqlalchemy_session: Session
    ) -> None:
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
            headers=self._auth_headers(sqlalchemy_session),
        )

        assert response.status_code == 422
