from unittest.mock import Mock
from uuid import uuid4
from typing import TYPE_CHECKING, cast

from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from src.equiny.core.auth.domain.entities.account import Account
from src.equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from src.equiny.core.profiling.domain.entities.dtos.owner_dto import OwnerDto
from src.equiny.core.profiling.domain.entities.owner import Owner
from src.equiny.pipes.ai_pipe import AiPipe
from src.equiny.providers.jwt import JoseJwtProvider
from src.equiny.database.sqlalchemy.repositories.auth.sqlalchemy_accounts_repository import (
    SqlalchemyAccountsRepository,
)
from src.equiny.database.sqlalchemy.repositories.profiling.sqlalchemy_owners_repository import (
    SqlalchemyOwnersRepository,
)
from tests.fakers.shared.structures.id_faker import IdFaker

if TYPE_CHECKING:
    from fastapi import FastAPI


class TestGenerateIcebreakerController:
    def _auth_headers(self, sqlalchemy_session: Session) -> tuple[dict[str, str], str]:
        account_email = f'generate-icebreaker-{uuid4().hex}@example.com'
        password_hash = PasswordHash.recommended().hash('plain-password')

        accounts_repo = SqlalchemyAccountsRepository(sqlalchemy_session)
        account = Account.create(
            AccountDto(email=account_email, password=password_hash, is_verified=True)
        )
        accounts_repo.add(account)
        sqlalchemy_session.flush()

        owners_repo = SqlalchemyOwnersRepository(sqlalchemy_session)
        owner = Owner.create(
            OwnerDto(
                name='Sender Owner',
                email=account_email,
                account_id=account.id.value,
                has_completed_onboarding=True,
            )
        )
        owners_repo.add(owner)
        sqlalchemy_session.commit()

        access_token = JoseJwtProvider().encode(account.id.value).access_token
        return ({'Authorization': f'Bearer {access_token}'}, owner.id.value)

    def test_should_require_jwt(
        self,
        client: TestClient,
    ) -> None:
        response = client.post(
            '/profiling/icebreaker',
            json={'recipient_owner_id': IdFaker.fake().value},
        )

        assert response.status_code == 401

    def test_should_generate_icebreaker_with_authenticated_sender_owner_id(
        self,
        client: TestClient,
        sqlalchemy_session: Session,
    ) -> None:
        headers, sender_owner_id = self._auth_headers(sqlalchemy_session)
        recipient_owner_id = IdFaker.fake().value

        workflow = Mock()
        workflow.run.return_value = 'Oi! Nossos cavalos combinam bastante.'
        fastapi_app = cast('FastAPI', client.app)

        fastapi_app.dependency_overrides[
            AiPipe.get_generate_icebreaker_workflow_from_request
        ] = lambda: workflow

        try:
            response = client.post(
                '/profiling/icebreaker',
                json={'recipient_owner_id': recipient_owner_id},
                headers=headers,
            )
        finally:
            fastapi_app.dependency_overrides.pop(
                AiPipe.get_generate_icebreaker_workflow_from_request,
                None,
            )

        assert response.status_code == 201
        assert response.json() == {'content': workflow.run.return_value}
        workflow.run.assert_called_once_with(
            sender_id=sender_owner_id,
            recipient_id=recipient_owner_id,
        )

    def test_should_return_422_when_recipient_owner_id_is_invalid(
        self,
        client: TestClient,
        sqlalchemy_session: Session,
    ) -> None:
        headers, _ = self._auth_headers(sqlalchemy_session)

        response = client.post(
            '/profiling/icebreaker',
            json={'recipient_owner_id': 'invalid-id'},
            headers=headers,
        )

        assert response.status_code == 422
