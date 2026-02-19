from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from equiny.core.profiling.domain.structures.breed import BreedValue
from equiny.core.profiling.domain.structures.sex import SexValue
from equiny.database.sqlalchemy.mappers.profiling.horses_mapper import HorsesMapper
from equiny.database.sqlalchemy.models.matching.match_model import MatchModel
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestListHorseMatchesController:
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
        auth_headers: dict[str, str],
        sqlalchemy_session: Session,
    ) -> None:
        horse_id, older_match_horse_id, newer_match_horse_id = self._seed_matches(
            sqlalchemy_session
        )

        response = client.get(
            f'/profiling/horses/{horse_id}/matches',
            headers=auth_headers,
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
        auth_headers: dict[str, str],
    ) -> None:
        response = client.get(
            '/profiling/horses/invalid-id/matches', headers=auth_headers
        )

        assert response.status_code == 422
