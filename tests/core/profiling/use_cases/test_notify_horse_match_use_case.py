import pytest
from unittest.mock import Mock, create_autospec

from src.equiny.core.profiling.domain.errors import (
    HorseMatchNotFoundError,
    OwnerNotFoundError,
)
from src.equiny.core.profiling.interfaces.repositories import (
    HorsesRepository,
    OwnersRepository,
)
from src.equiny.core.profiling.use_cases.notify_horse_match_use_case import (
    NotifyHorseMatchUseCase,
)
from src.equiny.core.shared.interfaces import Broker
from tests.fakers.profiling.entities.owners_faker import OwnersFaker
from tests.fakers.profiling.structures.horse_match_faker import HorseMatchFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestNotifyHorseMatchUseCase:
    horses_repository_mock: Mock
    owners_repository_mock: Mock
    broker_mock: Mock
    use_case: NotifyHorseMatchUseCase

    @pytest.fixture(autouse=True)
    def setup_tests(self) -> None:
        self.horses_repository_mock = create_autospec(HorsesRepository, instance=True)
        self.owners_repository_mock = create_autospec(OwnersRepository, instance=True)
        self.broker_mock = create_autospec(Broker, instance=True)
        self.use_case = NotifyHorseMatchUseCase(
            horses_repository=self.horses_repository_mock,
            owners_repository=self.owners_repository_mock,
            broker=self.broker_mock,
        )

    def test_should_publish_match_notifications_for_both_owners_when_horses_match_exists(
        self,
    ) -> None:
        horse_a_id = IdFaker.fake().value
        horse_b_id = IdFaker.fake().value
        horse_a_owner = OwnersFaker.fake()
        horse_b_owner = OwnersFaker.fake()
        horse_a_match = HorseMatchFaker.fake(owner_id=horse_a_owner.id.value)
        horse_b_match = HorseMatchFaker.fake(owner_id=horse_b_owner.id.value)
        self.horses_repository_mock.find_horse_match_by_horses.side_effect = [
            horse_a_match,
            horse_b_match,
        ]
        self.owners_repository_mock.find_by_id.side_effect = [
            horse_a_owner,
            horse_b_owner,
        ]

        self.use_case.execute(horse_a_id=horse_a_id, horse_b_id=horse_b_id)

        assert self.horses_repository_mock.find_horse_match_by_horses.call_count == 2
        first_horse_match_call = (
            self.horses_repository_mock.find_horse_match_by_horses.call_args_list[
                0
            ].kwargs
        )
        second_horse_match_call = (
            self.horses_repository_mock.find_horse_match_by_horses.call_args_list[
                1
            ].kwargs
        )
        assert first_horse_match_call['from_horse_id'].value == horse_a_id
        assert first_horse_match_call['to_horse_id'].value == horse_b_id
        assert second_horse_match_call['from_horse_id'].value == horse_b_id
        assert second_horse_match_call['to_horse_id'].value == horse_a_id

        assert self.owners_repository_mock.find_by_id.call_count == 2
        first_owner_id = self.owners_repository_mock.find_by_id.call_args_list[0][0][0]
        second_owner_id = self.owners_repository_mock.find_by_id.call_args_list[1][0][0]
        assert first_owner_id == horse_a_match.owner_id
        assert second_owner_id == horse_b_match.owner_id

        assert self.broker_mock.publish.call_count == 2
        first_event = self.broker_mock.publish.call_args_list[0][0][0]
        second_event = self.broker_mock.publish.call_args_list[1][0][0]
        assert first_event.horse_match == horse_a_match.dto
        assert first_event.owner_id == horse_b_owner.id.value
        assert second_event.horse_match == horse_b_match.dto
        assert second_event.owner_id == horse_a_owner.id.value

    def test_should_raise_horse_match_not_found_error_when_match_does_not_exist(
        self,
    ) -> None:
        horse_a_id = IdFaker.fake().value
        horse_b_id = IdFaker.fake().value
        self.horses_repository_mock.find_horse_match_by_horses.return_value = None

        with pytest.raises(HorseMatchNotFoundError):
            self.use_case.execute(horse_a_id=horse_a_id, horse_b_id=horse_b_id)

        self.horses_repository_mock.find_horse_match_by_horses.assert_called_once()
        self.owners_repository_mock.find_by_id.assert_not_called()
        self.broker_mock.publish.assert_not_called()

    def test_should_raise_owner_not_found_error_when_owner_does_not_exist(self) -> None:
        horse_a_id = IdFaker.fake().value
        horse_b_id = IdFaker.fake().value
        horse_a_match = HorseMatchFaker.fake()
        horse_b_match = HorseMatchFaker.fake()
        self.horses_repository_mock.find_horse_match_by_horses.side_effect = [
            horse_a_match,
            horse_b_match,
        ]
        self.owners_repository_mock.find_by_id.return_value = None

        with pytest.raises(OwnerNotFoundError):
            self.use_case.execute(horse_a_id=horse_a_id, horse_b_id=horse_b_id)

        assert self.horses_repository_mock.find_horse_match_by_horses.call_count == 2
        self.owners_repository_mock.find_by_id.assert_called_once_with(
            horse_a_match.owner_id
        )
        self.broker_mock.publish.assert_not_called()
