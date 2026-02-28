import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.matching.domain.errors.swipe_already_registered_error import (
    SwipeAlreadyRegisteredError,
)
from equiny.core.matching.domain.structures.swipe_decision import SwipeDecisionValue
from equiny.core.matching.interfaces import SwipesRepository, MatchesRepository
from equiny.core.matching.use_cases.swipe_horse_use_case import SwipeHorseUseCase
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.interfaces.broker import Broker
from tests.fakers.matching.structures.swipe_faker import SwipeFaker
from tests.fakers.profiling.structures.horse_match_faker import HorseMatchFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestSwipeHorseUseCase:
    swipes_repository_mock: Mock
    matches_repository_mock: Mock
    horses_repository_mock: Mock
    broker_mock: Mock
    use_case: SwipeHorseUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.swipes_repository_mock = create_autospec(SwipesRepository, instance=True)
        self.matches_repository_mock = create_autospec(MatchesRepository, instance=True)
        self.horses_repository_mock = create_autospec(HorsesRepository, instance=True)
        self.broker_mock = create_autospec(Broker, instance=True)
        self.swipes_repository_mock.find_by_horses.return_value = None
        self.use_case = SwipeHorseUseCase(
            swipes_repository=self.swipes_repository_mock,
            matches_repository=self.matches_repository_mock,
            horses_repository=self.horses_repository_mock,
            broker=self.broker_mock,
        )

    def test_should_create_swipe_and_add_it_to_repository(self) -> None:
        swipe_dto = SwipeFaker.fake_dto()

        result = self.use_case.execute(dto=swipe_dto)

        self.swipes_repository_mock.add.assert_called_once()
        captured_swipe = self.swipes_repository_mock.add.call_args[0][0]
        assert result == captured_swipe.dto
        assert result.from_horse_id == swipe_dto.from_horse_id
        assert result.to_horse_id == swipe_dto.to_horse_id
        assert result.decision == swipe_dto.decision

    def test_should_create_match_when_reverse_like_exists(self) -> None:
        from_horse_id = IdFaker.fake().value
        to_horse_id = IdFaker.fake().value
        reverse_swipe = SwipeFaker.fake(
            from_horse_id=to_horse_id,
            to_horse_id=from_horse_id,
            decision=SwipeDecisionValue.LIKE,
        )
        self.swipes_repository_mock.find_by_horses.side_effect = [
            None,
            reverse_swipe,
        ]
        self.horses_repository_mock.find_horse_match_by_horses.return_value = (
            HorseMatchFaker.fake()
        )

        swipe_dto = SwipeFaker.fake_dto(
            from_horse_id=from_horse_id,
            to_horse_id=to_horse_id,
            decision=SwipeDecisionValue.LIKE,
        )

        result = self.use_case.execute(dto=swipe_dto)

        self.matches_repository_mock.add.assert_called_once()
        captured_match = self.matches_repository_mock.add.call_args[0][0]
        assert captured_match.horse_a_id.value == from_horse_id
        assert captured_match.horse_b_id.value == to_horse_id
        self.swipes_repository_mock.add.assert_called_once()
        assert self.horses_repository_mock.find_horse_match_by_horses.call_count == 2
        self.broker_mock.publish.assert_called()

    def test_should_not_create_match_when_reverse_swipe_is_dislike(self) -> None:
        from_horse_id = IdFaker.fake().value
        to_horse_id = IdFaker.fake().value
        reverse_swipe = SwipeFaker.fake(
            from_horse_id=to_horse_id,
            to_horse_id=from_horse_id,
            decision=SwipeDecisionValue.DISLIKE,
        )
        self.swipes_repository_mock.find_by_horses.side_effect = [
            None,
            reverse_swipe,
        ]

        swipe_dto = SwipeFaker.fake_dto(
            from_horse_id=from_horse_id,
            to_horse_id=to_horse_id,
            decision=SwipeDecisionValue.LIKE,
        )

        result = self.use_case.execute(dto=swipe_dto)

        self.matches_repository_mock.add.assert_not_called()
        self.swipes_repository_mock.add.assert_called_once()

    def test_should_not_create_match_when_current_swipe_is_dislike(self) -> None:
        from_horse_id = IdFaker.fake().value
        to_horse_id = IdFaker.fake().value
        reverse_swipe = SwipeFaker.fake(
            from_horse_id=to_horse_id,
            to_horse_id=from_horse_id,
            decision=SwipeDecisionValue.LIKE,
        )
        self.swipes_repository_mock.find_by_horses.side_effect = [
            None,
            reverse_swipe,
        ]

        swipe_dto = SwipeFaker.fake_dto(
            from_horse_id=from_horse_id,
            to_horse_id=to_horse_id,
            decision=SwipeDecisionValue.DISLIKE,
        )

        result = self.use_case.execute(dto=swipe_dto)

        self.matches_repository_mock.add.assert_not_called()
        self.swipes_repository_mock.add.assert_called_once()

    def test_should_raise_error_when_swipe_already_registered(self) -> None:
        existing_swipe = SwipeFaker.fake()
        self.swipes_repository_mock.find_by_horses.return_value = existing_swipe

        swipe_dto = SwipeFaker.fake_dto(
            from_horse_id=existing_swipe.from_horse_id.value,
            to_horse_id=existing_swipe.to_horse_id.value,
        )

        with pytest.raises(SwipeAlreadyRegisteredError):
            self.use_case.execute(dto=swipe_dto)

        self.swipes_repository_mock.add.assert_not_called()
        self.matches_repository_mock.add.assert_not_called()
