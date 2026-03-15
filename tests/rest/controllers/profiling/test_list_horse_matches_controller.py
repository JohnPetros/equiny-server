from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from src.equiny.core.auth.domain.entities.account import Account
from src.equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from src.equiny.core.profiling.domain.structures.breed import BreedValue
from src.equiny.core.profiling.domain.structures.sex import SexValue
from src.equiny.database.sqlalchemy.repositories.auth.sqlalchemy_accounts_repository import (
    SqlalchemyAccountsRepository,
)
from src.equiny.database.sqlalchemy.mappers.profiling.horses_mapper import HorsesMapper
from src.equiny.database.sqlalchemy.models.matching.match_model import MatchModel
from src.equiny.providers.jwt import JoseJwtProvider
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestListHorseMatchesController:
    def _auth_headers(self, sqlalchemy_session: Session) -> dict[str, str]:
        account_email = f'list-matches-{uuid4().hex}@example.com'
        password_hash = PasswordHash.recommended().hash('plain-password')

        accounts_repo = SqlalchemyAccountsRepository(sqlalchemy_session)
        account = Account.create(
            AccountDto(
                email=account_email,
                password=password_hash,
                is_verified=True,
            )
        )
        accounts_repo.add(account)
        sqlalchemy_session.commit()

        access_token = JoseJwtProvider().encode(account.id.value).access_token
        return {'Authorization': f'Bearer {access_token}'}

    def _seed_matches(self, sqlalchemy_session: Session) -> tuple[str, str, str]:
        now = datetime.now()

        target_horse = HorsesMapper.to_model(
            HorsesFaker.fake(
                id=IdFaker.fake().value,
                breed=BreedValue.ARABE.value,
                sex=SexValue.MALE.value,
            )
        )
        older_match_horse = HorsesMapper.to_model(
            HorsesFaker.fake(
                id=IdFaker.fake().value,
                breed=BreedValue.ARABE.value,
                sex=SexValue.FEMALE.value,
            )
        )
        newer_match_horse = HorsesMapper.to_model(
            HorsesFaker.fake(
                id=IdFaker.fake().value,
                breed=BreedValue.ARABE.value,
                sex=SexValue.FEMALE.value,
            )
        )

        older_match = MatchModel(
            horse_a_id=target_horse.id,
            horse_b_id=older_match_horse.id,
            created_at=now - timedelta(days=1),
        )
        newer_match = MatchModel(
            horse_a_id=newer_match_horse.id,
            horse_b_id=target_horse.id,
            created_at=now,
        )

        sqlalchemy_session.add_all([target_horse, older_match_horse, newer_match_horse])
        sqlalchemy_session.flush()
        sqlalchemy_session.add_all([older_match, newer_match])
        sqlalchemy_session.commit()

        return target_horse.id, older_match_horse.id, newer_match_horse.id

    def test_should_return_horse_matches_sorted_by_created_at_desc(
        self,
        client: TestClient,
        sqlalchemy_session: Session,
    ) -> None:
        horse_id, older_match_horse_id, newer_match_horse_id = self._seed_matches(
            sqlalchemy_session
        )

        response = client.get(
            f'/profiling/horses/{horse_id}/matches',
            headers=self._auth_headers(sqlalchemy_session),
        )

        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 2
        assert payload[0]['owner_horse_id'] == newer_match_horse_id
        assert payload[1]['owner_horse_id'] == older_match_horse_id
        assert payload[0]['owner_horse_id'] != horse_id
        assert payload[1]['owner_horse_id'] != horse_id
        assert payload[0]['created_at'] > payload[1]['created_at']

    def test_should_return_422_when_horse_id_is_invalid(
        self,
        client: TestClient,
        sqlalchemy_session: Session,
    ) -> None:
        response = client.get(
            '/profiling/horses/invalid-id/matches',
            headers=self._auth_headers(sqlalchemy_session),
        )

        assert response.status_code == 422
