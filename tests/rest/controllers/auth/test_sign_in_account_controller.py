from fastapi.testclient import TestClient


class TestSignInAccountController:
    def test_should_sign_in_and_return_access_token_when_body_is_valid(
        self, client: TestClient
    ) -> None:
        response1 = client.post(
            '/auth/sign-up',
            json={
                'owner_name': 'John Owner',
                'account_email': 'signin-user@example.com',
                'account_password': 'plain-password',
            },
        )
        print('response1', response1.status_code)
        response = client.post(
            '/auth/sign-in',
            json={
                'email': 'signin-user@example.com',
                'password': 'plain-password',
            },
        )

        print(response)
        assert response.status_code == 201

        data = response.json()
        assert 'access_token' in data
        assert isinstance(data['access_token'], str)
        assert len(data['access_token']) > 0

    def test_should_return_422_when_email_is_invalid(self, client: TestClient) -> None:
        response = client.post(
            '/auth/sign-in',
            json={
                'email': 'invalid-email',
                'password': 'plain-password',
            },
        )

        assert response.status_code == 422
        assert response.json()['title'] == 'Erro de validação'

    def test_should_return_401_when_password_is_invalid(
        self, client: TestClient
    ) -> None:
        client.post(
            '/auth/sign-up',
            json={
                'owner_name': 'John Owner',
                'account_email': 'signin-wrong-password@example.com',
                'account_password': 'plain-password',
            },
        )

        response = client.post(
            '/auth/sign-in',
            json={
                'email': 'signin-wrong-password@example.com',
                'password': 'wrong-password',
            },
        )

        assert response.status_code == 401
        assert response.json()['message'] == 'Credenciais inválidas'
