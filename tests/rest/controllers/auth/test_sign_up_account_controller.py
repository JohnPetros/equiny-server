from fastapi.testclient import TestClient
from uuid import uuid4


class TestSignUpAccountController:
    def test_should_sign_up_account_and_return_payload_when_body_is_valid(
        self, client: TestClient
    ) -> None:
        account_email = f'signup-user-{uuid4().hex}@example.com'

        response = client.post(
            '/auth/sign-up',
            json={
                'owner_name': 'John Owner',
                'account_email': account_email,
                'account_password': 'plain-password',
            },
        )

        assert response.status_code == 201

        data = response.json()
        assert data['id']
        assert data['email'] == account_email
        assert 'password' not in data

    def test_should_return_422_when_owner_name_is_too_short(
        self, client: TestClient
    ) -> None:
        response = client.post(
            '/auth/sign-up',
            json={
                'owner_name': 'AB',
                'account_email': 'invalid-owner-name@example.com',
                'account_password': 'plain-password',
            },
        )

        assert response.status_code == 422

    def test_should_return_409_when_email_is_already_in_use(
        self, client: TestClient
    ) -> None:
        account_email = f'duplicate-{uuid4().hex}@example.com'
        payload = {
            'owner_name': 'John Owner',
            'account_email': account_email,
            'account_password': 'plain-password',
        }

        client.post('/auth/sign-up', json=payload)
        response = client.post('/auth/sign-up', json=payload)

        assert response.status_code == 409
        assert response.json()['message'] == f'Email {account_email} já está em uso'
