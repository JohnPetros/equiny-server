---
title: Verificacao de email da conta do usuario
prd: documentation/features/auth/sign-up/prd.md
status: concluida
last_updated_at: 2026-03-01
---

# 1. Objetivo

Implementar o fluxo completo de verificacao de email para contas criadas no sign-up. Apos o owner ser criado (via `CreateOwnerJob`), um job assincrono (`SendEmailVerificationJob`) envia um email de verificacao com link clicavel para o usuario. O endpoint `GET /auth/verify-email?token=<token>` valida o token e marca a conta como verificada (`is_verified=true`). Adicionalmente, um endpoint `POST /auth/resend-verification-email` permite o reenvio do email de verificacao com rate limit. Os providers concretos usam **itsdangerous** para gerar/validar tokens e **Mailtrap** para enviar emails.

# 2. Escopo

## 2.1 In-scope

- **Migration** para adicionar `is_verified` na tabela `accounts`.
- **Refatorar** `EmailProvider` para receber `(account_email, verification_token)`.
- **Implementar** `ItsdangerousEmailVerificationProvider` (gerar e validar tokens com TTL).
- **Implementar** `MailtrapEmailProvider` (enviar email de verificacao via API do Mailtrap).
- **Criar** `SendAccountVerificationEmailUseCase` no contexto `notification`.
- **Criar** `SendEmailVerificationJob` que escuta `OwnerCreatedEvent` e envia email.
- **Criar** endpoint `GET /auth/verify-email?token=<token>` para verificar a conta.
- **Criar** `VerifyAccountEmailUseCase` no contexto `auth`.
- **Criar** endpoint `POST /auth/resend-verification-email` para reenvio do email.
- **Criar** `ResendAccountVerificationEmailUseCase` no contexto `auth`.
- **Atualizar** `AccountModel`, `AccountsMapper` e `AccountsRepository` para suportar `is_verified` e `update`.
- **Registrar** env vars (`MAILTRAP_API_KEY`, `MAILTRAP_SENDER_EMAIL`, `EMAIL_VERIFICATION_SECRET`, `CLIENT_BASE_URL`) em `Env`.
- **Registrar** novos providers em `ProvidersPipe`.
- **Registrar** novo job em `InngestPubSub`.

## 2.2 Out-of-scope

- Bloqueio de funcionalidades para contas nao verificadas (guard global).
- Template HTML estilizado para o email (usar texto simples/HTML basico).
- Reenvio automatico por cron/agendamento.
- Testes automatizados.

## 2.3 Decisoes finais de implementacao

- O projeto passou a aplicar bloqueio para contas nao verificadas nas rotas protegidas via `AuthPipe.verify_jwt` (retorno 401 quando `account.is_verified` for falso).
- O retorno do `POST /auth/sign-up` foi mantido sem senha, usando `SignUpResultDto` (`id`, `email`, `is_verified`).
- Foram adicionados ajustes de testes unitarios e de controller para manter compatibilidade com o novo contrato de JWT (`JwtDto` com `access_token` e `refresh_token`) e com a verificacao de conta.

# 3. Requisitos

## 3.1 Funcionais

- **RF-01**: Apos o owner ser criado, o sistema envia automaticamente um email de verificacao com link clicavel.
- **RF-02**: O link de verificacao contem um token seguro com TTL configuravel (padrao: 24h).
- **RF-03**: Ao acessar o link, o token e validado e a conta e marcada como `is_verified=true`.
- **RF-04**: Token expirado ou invalido retorna erro claro ao usuario.
- **RF-05**: O usuario pode solicitar reenvio do email de verificacao.
- **RF-06**: O reenvio so e permitido para contas nao verificadas.

## 3.2 Nao funcionais

- **RNF-01**: Token de verificacao assinado com HMAC via `itsdangerous` (secret dedicado `EMAIL_VERIFICATION_SECRET`).
- **RNF-02**: Envio de email via API do Mailtrap (HTTP, nao SMTP).
- **RNF-03**: Envio de email e assincrono (job Inngest), nao bloqueia a request HTTP.
- **RNF-04**: Job de envio de email deve ser idempotente.

# 4. Regras de negocio e invariantes

- **RN-01**: Cada conta nasce com `is_verified=false`.
- **RN-02**: Um token de verificacao so e valido para o email codificado nele.
- **RN-03**: Token expira apos TTL configurado (padrao 24h).
- **RN-04**: Verificar uma conta ja verificada e uma operacao no-op (retorna sucesso sem alterar estado).
- **RN-05**: Reenvio de email so funciona para contas existentes e nao verificadas.
- **RN-06**: Reenvio gera novo token (o anterior e implicitamente invalidado pela expiracao natural).

# 5. O que ja existe (inventario)

## 5.1 Core (`src/equiny/core/`)

- **`Account`** (`src/equiny/core/auth/domain/entities/account.py`) — entidade com campos `email`, `password`, `is_verified`. Sera usada para persistir e consultar estado de verificacao.
- **`AccountDto`** (`src/equiny/core/auth/domain/entities/dtos/account_dto.py`) — DTO com `id`, `email`, `password`, `is_verified`. Usado no transporte entre camadas.
- **`AccountsRepository`** (`src/equiny/core/auth/interfaces/repositories/accounts_repository.py`) — interface com `add`, `add_many`, `find_by_email`, `find_by_id`. Sera estendida com `update`.
- **`EmailVerificationProvider`** (`src/equiny/core/auth/interfaces/providers/email_verification_provider.py`) — interface com `generate_verification_token(Email) -> Text` e `verify_verification_token(Text) -> Logical`. Sera implementada com `itsdangerous`.
- **`EmailProvider`** (`src/equiny/core/notification/interfaces/email_sender_provider.py`) — interface com `send_account_verification_email(Email) -> None`. **Sera refatorada** para receber `(Email, Text)`.
- **`AccountCreatedEvent`** (`src/equiny/core/auth/domain/events/account_created_event.py`) — evento que ja carrega `account_email_verification_token` no payload.
- **`OwnerCreatedEvent`** (`src/equiny/core/profiling/domain/events/owner_created_event.py`) — evento publicado pelo `CreateOwnerUseCase` com `owner_id`, `owner_email`, `owner_email_verification_token`. Sera o trigger do job de envio de email.
- **`SignUpAccountUseCase`** (`src/equiny/core/auth/use_cases/sign_up_account_use_case.py`) — ja gera o token de verificacao via `EmailVerificationProvider` e o passa no `AccountCreatedEvent`.
- **`CreateOwnerUseCase`** (`src/equiny/core/profiling/use_cases/create_owner_use_case.py`) — recebe o `owner_email_verification_token` e republica via `OwnerCreatedEvent`.

## 5.2 Database (`src/equiny/database/`)

- **`AccountModel`** (`src/equiny/database/sqlalchemy/models/auth/account_model.py`) — modelo ORM da tabela `accounts`. **Nao possui** `is_verified`; sera adicionado via migration.
- **`AccountsMapper`** (`src/equiny/database/sqlalchemy/mappers/auth/accounts_mapper.py`) — converte `AccountModel <-> Account/AccountDto`. **Nao mapeia** `is_verified`; sera atualizado.
- **`SqlalchemyAccountsRepository`** (`src/equiny/database/sqlalchemy/repositories/auth/sqlalchemy_accounts_repository.py`) — implementa `add`, `add_many`, `find_by_email`, `find_by_id`. **Nao possui** `update`; sera estendido.

## 5.3 REST/Controllers (`src/equiny/rest/controllers/auth/`)

- **`SignUpAccountController`** (`src/equiny/rest/controllers/auth/sign_up_account_controller.py`) — endpoint `POST /sign-up`. Nao sera alterado nesta spec.

## 5.4 Routers (`src/equiny/routers/auth/`)

- **`AuthRouter`** (`src/equiny/routers/auth/auth_router.py`) — registra `SignInAccountController` e `SignUpAccountController`. Sera estendido com novos controllers.

## 5.5 Pipes

- **`ProvidersPipe`** (`src/equiny/pipes/providers_pipe.py`) — fornece `HashProvider`, `JwtProvider`, `FileStorageProvider`, `CacheProvider`. Sera estendido com `EmailVerificationProvider` e `EmailProvider`.
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) — fornece repositorios via `Depends`. Ja possui `get_accounts_repository`.
- **`PubSubPipe`** (`src/equiny/pipes/pubsub_pipe.py`) — fornece `Broker` via `Depends`.

## 5.6 PubSub

- **`CreateOwnerJob`** (`src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`) — consome `AccountCreatedEvent` e executa `CreateOwnerUseCase`, que publica `OwnerCreatedEvent` com o token de verificacao.
- **`InngestPubSub`** (`src/equiny/pubsub/inngest/inngest_pubsub.py`) — composition root dos jobs Inngest. Sera estendido para registrar o novo job.

## 5.7 Constants

- **`Env`** (`src/equiny/constants/env.py`) — configuracoes via env vars. Sera estendida com novas variaveis.

# 6. O que deve ser criado

## 6.1 Core

### 6.1.1 Use Cases

- **Arquivo:** `src/equiny/core/notification/use_cases/send_account_verification_email_use_case.py` **(novo)**
  - **Use case:** `SendAccountVerificationEmailUseCase`
  - **Entrada:** `account_email: str`, `email_verification_token: str`
  - **Saida:** `None`
  - **Dependencias:** `EmailProvider`
  - **Fluxo:**
    1. Criar `Email.create(account_email)` e `Text.create(email_verification_token)`.
    2. Chamar `email_sender_provider.send_account_verification_email(email, token)`.

- **Arquivo:** `src/equiny/core/auth/use_cases/verify_account_email_use_case.py` **(novo)**
  - **Use case:** `VerifyAccountEmailUseCase`
  - **Entrada:** `verification_token: str`
  - **Saida:** `None`
  - **Dependencias:** `EmailVerificationProvider`, `AccountsRepository`
  - **Fluxo:**
    1. Chamar `email_verification_provider.verify_verification_token(Text.create(token))`.
    2. Se `Logical.is_false` -> levantar `InvalidEmailVerificationTokenError`.
    3. Decodificar o email do token via `email_verification_provider.decode_email_from_token(Text.create(token))`.
    4. Buscar conta via `repository.find_by_email(email)`.
    5. Se conta nao encontrada -> levantar `AccountNotFoundError`.
    6. Se `account.is_verified.is_true` -> retornar (no-op).
    7. Setar `account.is_verified = Logical.create_true()`.
    8. Chamar `repository.update(account)`.

- **Arquivo:** `src/equiny/core/auth/use_cases/resend_account_verification_email_use_case.py` **(novo)**
  - **Use case:** `ResendAccountVerificationEmailUseCase`
  - **Entrada:** `account_email: str`
  - **Saida:** `None`
  - **Dependencias:** `AccountsRepository`, `EmailVerificationProvider`, `Broker`
  - **Fluxo:**
    1. Buscar conta via `repository.find_by_email(account_email)`.
    2. Se conta nao encontrada -> levantar `AccountNotFoundError`.
    3. Se `account.is_verified.is_true` -> levantar `AccountAlreadyVerifiedError`.
    4. Gerar novo token via `email_verification_provider.generate_verification_token(account.email)`.
    5. Publicar `EmailVerificationRequestedEvent(account_email, token)` via `broker.publish(...)`.

### 6.1.2 Domain (Errors/Events)

- **Arquivo:** `src/equiny/core/auth/domain/errors/invalid_email_verification_token_error.py` **(novo)**
  - **Tipo:** `error`
  - **Responsabilidade:** sinalizar token de verificacao invalido ou expirado.
  - **Herda de:** `AuthError` (`src/equiny/core/shared/domain/errors/auth_error.py`)
  - **Mensagem:** `'Token de verificação de email inválido ou expirado'`

- **Arquivo:** `src/equiny/core/auth/domain/errors/account_already_verified_error.py` **(novo)**
  - **Tipo:** `error`
  - **Responsabilidade:** sinalizar tentativa de reenvio para conta ja verificada.
  - **Herda de:** `ConflictError` (`src/equiny/core/shared/domain/errors/conflict_error.py`)
  - **Mensagem:** `'Esta conta já foi verificada'`

- **Arquivo:** `src/equiny/core/auth/domain/events/email_verification_requested_event.py` **(novo)**
  - **Tipo:** `event`
  - **Responsabilidade:** sinalizar pedido de reenvio de email de verificacao.
  - **Payload:** `account_email: str`, `email_verification_token: str`
  - **`name`:** `'auth/email.verification.requested'`

### 6.1.3 Interfaces

- **Arquivo:** `src/equiny/core/auth/interfaces/providers/email_verification_provider.py` **(modificar)**
  - **Metodo adicional:** `decode_email_from_token(self, verification_token: Text) -> str`
  - **Semantica:** extrair o email codificado no token assinado para uso no `VerifyAccountEmailUseCase`.

## 6.2 Validation

- **Arquivo:** `src/equiny/validation/auth/resend_verification_email_schema.py` **(novo)**
  - **Schema:** `ResendVerificationEmailSchema`
  - **Campos:** `account_email: str` (reusa validacao de `EmailSchema`)
  - **Observacao:** schema simples para body do endpoint de reenvio.

## 6.3 Database

### 6.3.1 Models

- **Arquivo:** `src/equiny/database/sqlalchemy/models/auth/account_model.py` **(modificar)**
  - **Mudanca:** adicionar campo `is_verified: Mapped[bool] = mapped_column(default=False)`.

### 6.3.2 Mappers

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/auth/accounts_mapper.py` **(modificar)**
  - **Mudanca:** incluir `is_verified` em `to_entity`, `to_dto` e `to_model`.

### 6.3.3 Repositories

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/auth/sqlalchemy_accounts_repository.py` **(modificar)**
  - **Metodo adicional:** `update(self, account: Account) -> None`
  - **Implementacao:** buscar `AccountModel` por `id`, atualizar campos e usar `session.merge()` ou atualizar atributos.

### 6.3.4 Migracoes (Alembic)

- **Mudanca de schema:** adicionar coluna `is_verified BOOLEAN DEFAULT FALSE NOT NULL` na tabela `accounts`.
- **Nova migration:** `alembic/versions/<revision>_add_is_verified_to_accounts.py`

## 6.4 Providers (implementacoes concretas)

- **Arquivo:** `src/equiny/providers/auth/itsdangerous/itsdangerous_email_verification_provider.py` **(novo)**
  - **Classe:** `ItsdangerousEmailVerificationProvider`
  - **Implementa:** `EmailVerificationProvider`
  - **Dependencias:** `itsdangerous.URLSafeTimedSerializer`, `Env.EMAIL_VERIFICATION_SECRET`
  - **Comportamento:**
    - `generate_verification_token(email: Email) -> Text`: serializa `email.value` com `URLSafeTimedSerializer` e retorna `Text.create(token)`.
    - `verify_verification_token(token: Text) -> Logical`: tenta deserializar com `max_age` (padrao 86400s = 24h); retorna `Logical.create_true()` se valido, `Logical.create_false()` se `SignatureExpired` ou `BadSignature`.
    - `decode_email_from_token(token: Text) -> str`: deserializa o token e retorna o email embutido. Levanta excecao se invalido.

- **Arquivo:** `src/equiny/providers/notification/mailtrap/mailtrap_email_sender_provider.py` **(novo)**
  - **Classe:** `MailtrapEmailProvider`
  - **Implementa:** `EmailProvider`
  - **Dependencias:** `httpx` (ou `requests`), `Env.MAILTRAP_API_KEY`, `Env.MAILTRAP_SENDER_EMAIL`, `Env.CLIENT_BASE_URL`
  - **Comportamento:**
    - `send_account_verification_email(email: Email, token: Text) -> None`: monta URL `{CLIENT_BASE_URL}/auth/verify-email?token={token.value}`, envia email via API HTTP do Mailtrap com link de verificacao.

## 6.5 Pipes

- **Arquivo:** `src/equiny/pipes/providers_pipe.py` **(modificar)**
  - **Metodos adicionais:**
    - `get_email_verification_provider() -> EmailVerificationProvider`: retorna `ItsdangerousEmailVerificationProvider()`.
    - `get_email_provider() -> EmailProvider`: retorna `MailtrapEmailProvider()`.

## 6.6 PubSub (Jobs)

- **Arquivo:** `src/equiny/pubsub/inngest/jobs/notification/send_email_verification_job.py` **(novo)**
  - **Job:** `SendEmailVerificationJob`
  - **Trigger:** `OwnerCreatedEvent.NAME` (`'profiling/owner.created'`)
  - **`fn_id`:** `'notification/send.email.verification.job'`
  - **PayloadSchema:** `owner_email: str`, `owner_email_verification_token: str`
  - **Fluxo:**
    1. Validar payload via `PayloadSchema.model_validate(context.event.data)`.
    2. `context.step.run('Send verification email', ...)`.
    3. Instanciar `MailtrapEmailProvider`.
    4. Instanciar `SendAccountVerificationEmailUseCase(email_sender_provider)`.
    5. Chamar `use_case.execute(owner_email, owner_email_verification_token)`.

- **Arquivo:** `src/equiny/pubsub/inngest/jobs/notification/resend_email_verification_job.py` **(novo)**
  - **Job:** `ResendEmailVerificationJob`
  - **Trigger:** `EmailVerificationRequestedEvent.name` (`'auth/email.verification.requested'`)
  - **`fn_id`:** `'notification/resend.email.verification.job'`
  - **PayloadSchema:** `account_email: str`, `email_verification_token: str`
  - **Fluxo:**
    1. Validar payload via `PayloadSchema.model_validate(context.event.data)`.
    2. `context.step.run('Resend verification email', ...)`.
    3. Instanciar `MailtrapEmailProvider`.
    4. Instanciar `SendAccountVerificationEmailUseCase(email_sender_provider)`.
    5. Chamar `use_case.execute(account_email, email_verification_token)`.

## 6.7 REST

### 6.7.1 Controllers

- **Arquivo:** `src/equiny/rest/controllers/auth/verify_account_email_controller.py` **(novo)**
  - **Controller:** `VerifyAccountEmailController`
  - **Rota (relativa):** `/verify-email`
  - **Metodo HTTP:** `GET`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `None` (sem body; retorna mensagem de sucesso)
  - **Query params:** `token: str`
  - **Dependencias:**
    - `AccountsRepository` via `Depends(DatabasePipe.get_accounts_repository)`
    - `EmailVerificationProvider` via `Depends(ProvidersPipe.get_email_verification_provider)`
  - **Fluxo:**
    1. Instanciar `VerifyAccountEmailUseCase(email_verification_provider, repository)`.
    2. Chamar `use_case.execute(token)`.
    3. Retornar `{'message': 'Email verificado com sucesso'}`.

- **Arquivo:** `src/equiny/rest/controllers/auth/resend_account_verification_email_controller.py` **(novo)**
  - **Controller:** `ResendAccountVerificationEmailController`
  - **Rota (relativa):** `/resend-verification-email`
  - **Metodo HTTP:** `POST`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `None`
  - **Body:** `ResendVerificationEmailSchema` com `account_email`
  - **Dependencias:**
    - `AccountsRepository` via `Depends(DatabasePipe.get_accounts_repository)`
    - `EmailVerificationProvider` via `Depends(ProvidersPipe.get_email_verification_provider)`
    - `Broker` via `Depends(PubSubPipe.get_broker_from_request)`
  - **Fluxo:**
    1. Instanciar `ResendAccountVerificationEmailUseCase(repository, email_verification_provider, broker)`.
    2. Chamar `use_case.execute(body.account_email)`.
    3. Retornar `{'message': 'Email de verificação reenviado'}`.

## 6.8 Routers

- **Arquivo:** `src/equiny/routers/auth/auth_router.py` **(modificar)**
  - **Mudanca:** registrar `VerifyAccountEmailController.handle(router)` e `ResendAccountVerificationEmailController.handle(router)`.

# 7. O que deve ser modificado

- **Arquivo:** `src/equiny/core/notification/interfaces/email_sender_provider.py`
  - **Mudanca:** alterar assinatura de `send_account_verification_email(self, account_email: Email) -> None` para `send_account_verification_email(self, account_email: Email, verification_token: Text) -> None`.
  - **Justificativa:** o provider precisa do token para montar o link de verificacao no email.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/auth/interfaces/providers/email_verification_provider.py`
  - **Mudanca:** adicionar metodo `decode_email_from_token(self, verification_token: Text) -> str` ao `Protocol`.
  - **Justificativa:** o `VerifyAccountEmailUseCase` precisa extrair o email do token para buscar a conta.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/auth/interfaces/repositories/accounts_repository.py`
  - **Mudanca:** adicionar metodo `update(self, account: Account) -> None` ao `Protocol`.
  - **Justificativa:** necessario para persistir a alteracao de `is_verified`.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/database/sqlalchemy/models/auth/account_model.py`
  - **Mudanca:** adicionar `is_verified: Mapped[bool] = mapped_column(default=False)`.
  - **Justificativa:** a tabela `accounts` nao possui essa coluna.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/auth/accounts_mapper.py`
  - **Mudanca:** incluir `is_verified` em `to_entity`, `to_dto` e `to_model`.
  - **Justificativa:** manter consistencia entre modelo e entidade.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/auth/sqlalchemy_accounts_repository.py`
  - **Mudanca:** implementar metodo `update(self, account: Account) -> None`.
  - **Justificativa:** necessario para persistir `is_verified=true`.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/pipes/providers_pipe.py`
  - **Mudanca:** adicionar `get_email_verification_provider()` e `get_email_provider()`.
  - **Justificativa:** expor os novos providers via `Depends(...)` para controllers.
  - **Camada:** `pipes`

- **Arquivo:** `src/equiny/routers/auth/auth_router.py`
  - **Mudanca:** registrar `VerifyAccountEmailController.handle(router)` e `ResendAccountVerificationEmailController.handle(router)`.
  - **Justificativa:** expor novos endpoints em `/auth/`.
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/pubsub/inngest/inngest_pubsub.py`
  - **Mudanca:** adicionar `register_notification_jobs(inngest)` e incluir `SendEmailVerificationJob.handle(inngest)` e `ResendEmailVerificationJob.handle(inngest)` na lista de `functions`.
  - **Justificativa:** registrar os novos jobs para que o Inngest os execute.
  - **Camada:** `pubsub`

- **Arquivo:** `src/equiny/constants/env.py`
  - **Mudanca:** adicionar `MAILTRAP_API_KEY: str`, `MAILTRAP_SENDER_EMAIL: str`, `EMAIL_VERIFICATION_SECRET: str`, `CLIENT_BASE_URL: str`.
  - **Justificativa:** configuracoes necessarias para os providers de email e token.
  - **Camada:** `constants`

- **Arquivo:** `src/equiny/core/auth/domain/errors/__init__.py`
  - **Mudanca:** exportar `InvalidEmailVerificationTokenError` e `AccountAlreadyVerifiedError`.
  - **Justificativa:** manter `__all__` atualizado.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/auth/use_cases/__init__.py`
  - **Mudanca:** exportar `VerifyAccountEmailUseCase` e `ResendAccountVerificationEmailUseCase`.
  - **Justificativa:** manter `__all__` atualizado.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/notification/use_cases/__init__.py`
  - **Mudanca:** exportar `SendAccountVerificationEmailUseCase`.
  - **Justificativa:** manter `__all__` atualizado.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/rest/controllers/auth/__init__.py`
  - **Mudanca:** exportar `VerifyAccountEmailController` e `ResendAccountVerificationEmailController`.
  - **Justificativa:** manter `__all__` atualizado.
  - **Camada:** `rest`

# 8. O que deve ser removido

Nenhuma remocao necessaria.

# 9. Fluxo e diagramas

## 9.1 Fluxo de envio de email (sign-up)

```text
Client (Sign-up)
  -> POST /auth/sign-up
  -> SignUpAccountUseCase
      -> EmailVerificationProvider.generate_verification_token(email)
      -> Broker.publish(AccountCreatedEvent{..., token})

Inngest (profiling/create.owner.job)
  <- auth/account.created
  -> CreateOwnerUseCase
      -> OwnersRepository.add(owner)
      -> Broker.publish(OwnerCreatedEvent{owner_email, token})

Inngest (notification/send.email.verification.job)
  <- profiling/owner.created
  -> SendAccountVerificationEmailUseCase
      -> EmailProvider.send_account_verification_email(email, token)
  -> Email enviado com link: {CLIENT_BASE_URL}/auth/verify-email?token=<token>
```

## 9.2 Fluxo de verificacao de email

```text
Client (clica no link do email)
  -> GET /auth/verify-email?token=<token>
  -> VerifyAccountEmailController
  -> VerifyAccountEmailUseCase
      -> EmailVerificationProvider.verify_verification_token(token) -> Logical
      -> EmailVerificationProvider.decode_email_from_token(token) -> email
      -> AccountsRepository.find_by_email(email) -> Account
      -> account.is_verified = Logical.create_true()
      -> AccountsRepository.update(account)
  -> HTTP 200 { message: "Email verificado com sucesso" }
```

## 9.3 Fluxo de reenvio de email

```text
Client
  -> POST /auth/resend-verification-email { account_email }
  -> ResendAccountVerificationEmailController
  -> ResendAccountVerificationEmailUseCase
      -> AccountsRepository.find_by_email(email) -> Account
      -> (se nao encontrada -> 404)
      -> (se ja verificada -> 409)
      -> EmailVerificationProvider.generate_verification_token(account.email)
      -> Broker.publish(EmailVerificationRequestedEvent{email, token})
  -> HTTP 201 { message: "Email de verificação reenviado" }

Inngest (notification/resend.email.verification.job)
  <- auth/email.verification.requested
  -> SendAccountVerificationEmailUseCase
      -> EmailProvider.send_account_verification_email(email, token)
```

## 9.4 Referencias internas

- `src/equiny/rest/controllers/auth/sign_up_account_controller.py` (padrao de controller auth)
- `src/equiny/core/auth/use_cases/sign_up_account_use_case.py` (padrao de use case auth com providers)
- `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py` (padrao de job Inngest)
- `src/equiny/providers/jwt/jose/jose_jwt_provider.py` (padrao de provider concreto)
- `src/equiny/providers/notification/onesignal/onesignal_push_notification_provider.py` (padrao de provider de notificacao)
- `src/equiny/core/notification/use_cases/send_horse_match_push_notification_use_case.py` (padrao de use case no contexto notification)
