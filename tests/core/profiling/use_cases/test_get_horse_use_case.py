import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.profiling.domain.errors import HorseNotFoundError
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.get_horse_use_case import GetHorseUseCase
from tests.fakers.profiling.entities.horses_faker import HorsesFaker


class TestGetHorseUseCase:
    repository_mock: Mock
    use_case: GetHorseUseCase

    @pytest.fixture(autouse=True)
    def setup_tests(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.use_case = GetHorseUseCase(repository=self.repository_mock)

    def test_should_return_horse_dto_when_horse_exists(self) -> None:
        horse = HorsesFaker.fake()
        self.repository_mock.find_by_id.return_value = horse

        result = self.use_case.execute(horse_id=horse.id.value)

        self.repository_mock.find_by_id.assert_called_once_with(horse.id.value)
        assert result == horse.dto

    def test_should_raise_horse_not_found_error_when_horse_does_not_exist(self) -> None:
        self.repository_mock.find_by_id.return_value = None

        with pytest.raises(HorseNotFoundError):
            self.use_case.execute(horse_id='missing-horse-id')

        self.repository_mock.find_by_id.assert_called_once_with('missing-horse-id')
