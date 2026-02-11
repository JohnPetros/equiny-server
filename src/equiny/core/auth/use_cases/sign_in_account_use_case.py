from equiny.core.auth.domain.entities.account import AccountDto


class SignInAccountUseCase:
    def execute(self, email: str, password: str) -> AccountDto:
        return AccountDto(email=email, password=password)
