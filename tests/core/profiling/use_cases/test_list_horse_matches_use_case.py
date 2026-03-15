import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.list_horse_matches_use_case import (
    ListHorseMatchesUseCase,
)
from tests.fakers.profiling.structures.horse_match_faker import HorseMatchFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestListHorseMatchesUseCase:
    repository_mock: Mock
    use_case: ListHorseMatchesUseCase

    @pytest.fixture(autouse=True)
    def setup_tests(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.use_case = ListHorseMatchesUseCase(repository=self.repository_mock)

    def test_should_return_horse_matches_when_repository_returns_matches(self) -> None:
        horse_match = HorseMatchFaker.fake()
        horse_id = IdFaker.fake().value
        self.repository_mock.find_all_matches.return_value = [horse_match]

        result = self.use_case.execute(horse_id=horse_id)

        self.repository_mock.find_all_matches.assert_called_once()
        searched_horse_id = self.repository_mock.find_all_matches.call_args[0][0]
        assert searched_horse_id.value == horse_id
        assert len(result) == 1
        assert result[0].dto == horse_match.dto

    def test_should_return_empty_list_when_repository_returns_no_matches(self) -> None:
        horse_id = IdFaker.fake().value
        self.repository_mock.find_all_matches.return_value = []

        result = self.use_case.execute(horse_id=horse_id)

        self.repository_mock.find_all_matches.assert_called_once()
        searched_horse_id = self.repository_mock.find_all_matches.call_args[0][0]
        assert searched_horse_id.value == horse_id
        assert result == []
