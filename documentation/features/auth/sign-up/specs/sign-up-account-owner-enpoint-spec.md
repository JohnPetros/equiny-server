---
title: Endpoint de sign-up (conta + owner)
application: server
status: em progresso
---

# 1. Objetivo

Entregar o endpoint `POST /auth/sign-up` para cadastrar uma conta com `owner_name`,
`account_email` e `account_password`, iniciar sessao via JWT e disparar a criacao
do owner no contexto de profiling. A entrega deve alinhar o contrato HTTP ao PRD
de sign-up, remover inconsistencias do fluxo atual (ordem de argumentos, payload
de evento e exposicao de senha) e manter a arquitetura (controller fino,
orquestracao no use case, persistencia no repository, side effect no broker/job).

# 2. O que ja existe?

## Camada REST (Controllers + Routers)

- **`SignUpAccountController`** (`src/equiny/rest/controllers/auth/sign_up_account_controller.py`) - endpoint `/sign-up` ja existe com DI de repository/hash/jwt/broker, mas o use case e chamado com ordem de argumentos incorreta.
- **`AuthRouter`** (`src/equiny/routers/auth/auth_router.py`) - registra apenas `SignInAccountController`; `SignUpAccountController` ainda nao e incluido.
- **`SignInAccountController`** (`src/equiny/rest/controllers/auth/sign_in_account_controller.py`) - referencia de padrao de controller no modulo auth.

## Camada Core (Auth)

- **`SignUpAccountUseCase`** (`src/equiny/core/auth/use_cases/sign_up_account_use_case.py`) - gera hash, cria account e publica `AccountCreatedEvent`; recebe `JwtProvider` mas nao usa.
- **`Account` / `AccountDto`** (`src/equiny/core/auth/domain/entities/account.py`, `src/equiny/core/auth/domain/entities/dtos/account_dto.py`) - entidade e DTO atuais retornam senha, o que nao atende ao PRD.
- **`AccountCreatedEvent`** (`src/equiny/core/auth/domain/events/account_created_event.py`) - payload atual inclui `account_id` e `owner_name`.

## Camada PubSub / Jobs

- **`CreateOwnerJob`** (`src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`) - consome `auth/account.created` e espera `owner_name`, `owner_email` e `account_id`; hoje existe mismatch porque o evento de auth nao envia `owner_email`.

## Camada Database

- **`AccountsRepository`** (`src/equiny/core/auth/interfaces/repositories/accounts_repository.py`) - possui `add` e `find_by_id`; nao ha busca por email para evitar duplicidade.
- **`SqlalchemyAccountsRepository`** (`src/equiny/database/sqlalchemy/repositories/auth/sqlalchemy_accounts_repository.py`) - implementa persistencia de account sem `find_by_email`.
- **`AccountModel`** (`src/equiny/database/sqlalchemy/models/auth/account_model.py`) - `email` ainda sem restricao explicita de unicidade.

## Camada Validation

- **`NameSchema` / `EmailSchema`** (`src/equiny/validation/shared/name_schema.py`, `src/equiny/validation/shared/email_schema.py`) - validacoes basicas reutilizaveis para sign-up.


## Camada REST (Controllers)

- **Arquivo:** `src/equiny/rest/controllers/auth/sign_up_account_controller.py`
- **Mudanca:** substituir schema inline por `SignUpAccountSchema`; usar
  `response_model` de sign-up sem senha; chamar `SignUpAccountUseCase.execute`
  com argumentos nomeados/DTO para evitar erro de ordem.

- **Arquivo:** `src/equiny/rest/controllers/auth/__init__.py`
- **Mudanca:** exportar `SignUpAccountController` em `__all__`.

## Camada Routers

- **Arquivo:** `src/equiny/routers/auth/auth_router.py`
- **Mudanca:** registrar `SignUpAccountController.handle(router)` junto do
  `SignInAccountController`.

## Camada Core (Use Cases)

- **Arquivo:** `src/equiny/core/auth/use_cases/sign_up_account_use_case.py`
- **Mudanca:**
  - verificar duplicidade por email antes de criar conta
  - gerar token JWT com `jwt_provider.encode(account.id.value)`
  - publicar `AccountCreatedEvent` com `owner_email`
  - retornar `SignUpResultDto` (sem senha)

## Camada Core (Events)

- **Arquivo:** `src/equiny/core/auth/domain/events/account_created_event.py`
- **Mudanca:** incluir `owner_email` no payload e no construtor do evento.

## Camada Core (Interfaces)

- **Arquivo:** `src/equiny/core/auth/interfaces/repositories/accounts_repository.py`
- **Mudanca:** adicionar contrato `find_by_email(email: str) -> Account | None`.

- **Arquivo:** `src/equiny/core/auth/domain/entities/dtos/__init__.py`
- **Mudanca:** exportar `SignUpResultDto`.

## Camada Database (Repositories + Models)

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/auth/sqlalchemy_accounts_repository.py`
- **Mudanca:** implementar `find_by_email` via query por `AccountModel.email`.

- **Arquivo:** `src/equiny/database/sqlalchemy/models/auth/account_model.py`
- **Mudanca:** aplicar restricao de unicidade no campo `email` (e indice).

## Camada Database (Migrations)

- **Arquivo:** `alembic/versions/<revision>_add_unique_constraint_to_accounts_email.py`
- **Mudanca:** criar migration para `UNIQUE` em `accounts.email`.

## Camada PubSub

- **Arquivo:** `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`
- **Mudanca:** manter `PayloadSchema` alinhado ao novo payload do evento (agora
  totalmente consistente com auth).

## Camada App/Error Mapping

- **Arquivo:** `src/equiny/app.py` (ou handler dedicado em `src/equiny/rest/`)
- **Mudanca:** mapear erro de email duplicado para `HTTP 409`, preservando
  resposta clara para o cliente.

# 5. O que deve ser removido?

## Camada REST (Controllers)

- **Arquivo:** `src/equiny/rest/controllers/auth/sign_up_account_controller.py`
- **Mudanca:** remover dependencia de `BodySchema` inline apos migracao para
  `validation/auth/sign_up_account_schema.py`.

## Camada Core/Auth

- **Arquivo:** `src/equiny/core/auth/domain/entities/dtos/account_dto.py`
- **Mudanca:** remover uso de `AccountDto` como response model de sign-up (manter
  `AccountDto` apenas para transporte interno, sem exposicao de senha na borda).

# 6. Diagramas e Referencias

- **Fluxo de Dados (ASCII):**

```text
Client (Sign-up form)
  -> POST /auth/sign-up
  -> SignUpAccountController (REST)
  -> SignUpAccountUseCase (Core)
      -> AccountsRepository.find_by_email
      -> HashProvider.generate
      -> AccountsRepository.add
      -> JwtProvider.encode
      -> Broker.publish(auth/account.created)
  -> HTTP 201 (account_id, account_email, access_token)

Inngest Function (profiling/create.owner.job)
  <- auth/account.created(account_id, owner_name, owner_email)
  -> CreateOwnerUseCase
  -> OwnersRepository.add
```

- **Layout (ASCII - contrato da API):**

```text
POST /auth/sign-up
request:
  owner_name
  account_email
  account_password
  account_confirm_password

response 201:
  account_id
  account_email
  access_token
```

- **Referencias:**
  - `src/equiny/rest/controllers/profiling/create_horse_controller.py`
  - `src/equiny/routers/profiling/horses_router.py`
  - `src/equiny/core/profiling/use_cases/create_owner_use_case.py`
  - `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`
