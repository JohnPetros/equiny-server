import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.matching.domain.errors import MatchNotFoundError
from equiny.core.matching.interfaces import MatchesRepository
from equiny.core.matching.use_cases.dismatch_horse_use_case import DismatchHorseUseCase
from tests.fakers.matching.structures.match_faker import MatchFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestDismatchHorseUseCase:
    matches_repository_mock: Mock
    use_case: DismatchHorseUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.matches_repository_mock = create_autospec(MatchesRepository, instance=True)
        self.use_case = DismatchHorseUseCase(
            matches_repository=self.matches_repository_mock
        )

    def test_should_remove_match_when_match_exists(self) -> None:
        match = MatchFaker.fake()
        self.matches_repository_mock.find_by_horses.return_value = match

        self.use_case.execute(
            horse_a_id=match.horse_a_id.value, horse_b_id=match.horse_b_id.value
        )

        self.matches_repository_mock.find_by_horses.assert_called_once_with(
            match.horse_a_id, match.horse_b_id
        )
        self.matches_repository_mock.remove.assert_called_once_with(match)

    def test_should_raise_match_not_found_error_when_match_does_not_exist(self) -> None:
        horse_a_id = IdFaker.fake().value
        horse_b_id = IdFaker.fake().value
        self.matches_repository_mock.find_by_horses.return_value = None

        with pytest.raises(MatchNotFoundError):
            self.use_case.execute(horse_a_id=horse_a_id, horse_b_id=horse_b_id)

        self.matches_repository_mock.find_by_horses.assert_called_once()
        self.matches_repository_mock.remove.assert_not_called()
