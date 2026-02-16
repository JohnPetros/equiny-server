import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.create_horse_use_case import CreateHorseUseCase
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestCreateHorseUseCase:
    repository_mock: Mock
    use_case: CreateHorseUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.repository_mock.find_by_id.return_value = None
        self.use_case = CreateHorseUseCase(repository=self.repository_mock)

    def test_should_create_horse_and_add_it_to_repository(self) -> None:
        horse_dto = HorsesFaker.fake_dto()
        owner_id = IdFaker.fake().value
        result = self.use_case.execute(horse_dto=horse_dto, owner_id=owner_id)

        self.repository_mock.add.assert_called_once()

        captured_horse = self.repository_mock.add.call_args[0][0]
        captured_owner_id = self.repository_mock.add.call_args[0][1]

        assert result == captured_horse.dto
        assert result.id is not None
        assert result.name == horse_dto.name
        assert result.birth_month == horse_dto.birth_month
        assert result.birth_year == horse_dto.birth_year
        assert result.breed == captured_horse.dto.breed
        assert result.sex == horse_dto.sex
        assert result.location == horse_dto.location
        assert captured_owner_id.value == owner_id
