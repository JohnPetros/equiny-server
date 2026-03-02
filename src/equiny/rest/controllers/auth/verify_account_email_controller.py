from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from equiny.core.auth.domain.errors.account_not_found_error import AccountNotFoundError
from equiny.core.auth.domain.errors.invalid_email_verification_token_error import (
    InvalidEmailVerificationTokenError,
)
from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.use_cases.verify_account_email_use_case import (
    VerifyAccountEmailUseCase,
)
from equiny.pipes import DatabasePipe, ProvidersPipe

_SUCCESS_HTML = """
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Equiny — E-mail verificado</title>
    <style>
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        font-family: system-ui, sans-serif;
        background: #f5f7fa;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 1.5rem;
      }
      .card {
        background: #fff;
        border-radius: 1rem;
        box-shadow: 0 4px 24px rgba(0,0,0,.08);
        padding: 2.5rem 2rem;
        max-width: 420px;
        width: 100%;
        text-align: center;
      }
      .icon { font-size: 3rem; margin-bottom: 1rem; }
      h1 { font-size: 1.5rem; color: #111827; margin-bottom: .5rem; }
      p  { font-size: 1rem;   color: #6b7280; line-height: 1.6; }
    </style>
  </head>
  <body>
    <div class="card">
      <div class="icon">✅</div>
      <h1>E-mail verificado com sucesso!</h1>
      <p>Sua conta foi confirmada. Você já pode fechar esta página e fazer login no aplicativo.</p>
    </div>
  </body>
</html>
"""

_ERROR_HTML = """
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Equiny — Erro na verificação</title>
    <style>
      *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{
        font-family: system-ui, sans-serif;
        background: #f5f7fa;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 1.5rem;
      }}
      .card {{
        background: #fff;
        border-radius: 1rem;
        box-shadow: 0 4px 24px rgba(0,0,0,.08);
        padding: 2.5rem 2rem;
        max-width: 420px;
        width: 100%;
        text-align: center;
      }}
      .icon {{ font-size: 3rem; margin-bottom: 1rem; }}
      h1 {{ font-size: 1.5rem; color: #111827; margin-bottom: .5rem; }}
      p  {{ font-size: 1rem;   color: #6b7280; line-height: 1.6; }}
    </style>
  </head>
  <body>
    <div class="card">
      <div class="icon">❌</div>
      <h1>Falha na verificação</h1>
      <p>{message}</p>
    </div>
  </body>
</html>
"""


class VerifyAccountEmailController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/verify-email',
            status_code=HTTPStatus.OK,
            response_class=HTMLResponse,
        )
        def _(
            token: str,
            repository: AccountsRepository = Depends(
                DatabasePipe.get_accounts_repository
            ),
            email_verification_provider: EmailVerificationProvider = Depends(
                ProvidersPipe.get_email_verification_provider
            ),
        ) -> HTMLResponse:
            use_case = VerifyAccountEmailUseCase(
                email_verification_provider=email_verification_provider,
                repository=repository,
            )
            try:
                use_case.execute(token)
                return HTMLResponse(
                    content=_SUCCESS_HTML,
                    status_code=HTTPStatus.OK,
                )
            except (InvalidEmailVerificationTokenError, AccountNotFoundError) as error:
                return HTMLResponse(
                    content=_ERROR_HTML.format(message=str(error)),
                    status_code=HTTPStatus.BAD_REQUEST,
                )
