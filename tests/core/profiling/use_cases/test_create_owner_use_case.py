from unittest.mock import Mock, create_autospec

import pytest

from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.use_cases.create_owner_use_case import CreateOwnerUseCase
from equiny.core.shared.domain.errors import ValidationError
from equiny.core.shared.interfaces import Broker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestCreateOwnerUseCase:
    repository_mock: Mock
    broker_mock: Mock
    use_case: CreateOwnerUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(OwnersRepository, instance=True)
        self.broker_mock = create_autospec(Broker, instance=True)
        self.use_case = CreateOwnerUseCase(
            repository=self.repository_mock,
            broker=self.broker_mock,
        )

    def test_should_create_owner_and_add_it_to_repository(self) -> None:
        account_id = IdFaker.fake().value

        result = self.use_case.execute(
            owner_name='John Owner',
            owner_email='john.owner@example.com',
            owner_email_verification_token='verification-token',
            account_id=account_id,
        )

        self.repository_mock.add.assert_called_once()
        self.broker_mock.publish.assert_called_once()
        captured_owner = self.repository_mock.add.call_args[0][0]

        assert result == captured_owner.dto
        assert result.id is not None
        assert result.name == 'John Owner'
        assert result.email == 'john.owner@example.com'
        assert result.account_id == account_id
        assert result.has_completed_onboarding is False

    def test_should_raise_validation_error_when_owner_email_is_invalid(self) -> None:
        account_id = IdFaker.fake().value

        with pytest.raises(ValidationError):
            self.use_case.execute(
                owner_name='John Owner',
                owner_email='invalid-email',
                owner_email_verification_token='verification-token',
                account_id=account_id,
            )

        self.repository_mock.add.assert_not_called()
        self.broker_mock.publish.assert_not_called()
