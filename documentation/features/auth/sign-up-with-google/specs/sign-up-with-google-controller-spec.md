---
title: Controller de cadastro/login com Google
prd: ../prd.md
status: concluido
last_updated_at: 2026-03-15
---

# 1. Objetivo

Entregar o endpoint `POST /auth/sign-up/google` para receber um `id_token` do Google, validar a identidade no backend, criar ou vincular a `Account` existente sem duplicidade, publicar `AccountCreatedEvent` quando a conta for nova e retornar `JwtDto` imediatamente para o app seguir ao onboarding. A implementacao deve reutilizar os padroes atuais de `AuthRouter`, `Depends(...)`, `UseCase`, broker por evento e DTOs do `core`, sem colocar regra de negocio no controller e sem acoplar o caso de uso de auth a repositarios do dominio de profiling.

# 2. Escopo

## 2.1 In-scope

- Criar um endpoint HTTP para autenticar cadastro/login via Google a partir de `id_token`.
- Validar `id_token` com um unico audience configurado em `Env.GOOGLE_OAUTH_CLIENT_ID`.
- Criar `Account` nova com `is_verified = true`, `password = None` e provedor `google` quando o email nao existir.
- Vincular o provedor `google` a uma `Account` existente quando o email ja estiver cadastrado.
- Marcar `Account.is_verified = true` durante a vinculacao de conta existente.
- Disparar `AccountCreatedEvent` para que a criacao do `Owner` continue acontecendo pelo fluxo assincrono existente quando a conta for nova.
- Persistir provedores sociais de forma estruturada no banco.
- Ajustar o login por email/senha para falhar com mensagem informativa quando a conta nao possuir senha.

## 2.2 Out-of-scope

- Login social com Apple, Facebook ou outros provedores.
- Desvinculacao de conta Google ja associada.
- Tela de gerenciamento de provedores vinculados.
- Refresh token OAuth do Google.
- Alteracao do fluxo atual de `POST /auth/sign-up` com senha, alem dos ajustes necessarios para manter compatibilidade com `password = None` e `social_accounts`.
- Qualquer mudanca em push, notificacoes, chat ou onboarding alem da reutilizacao do fluxo assincrono ja existente de criacao de `Owner`.

# 3. Requisitos

## 3.1 Funcionais

- O backend deve expor `POST /auth/sign-up/google` com body contendo `id_token`.
- O endpoint deve validar o token do Google e extrair pelo menos `email` e `name`.
- Se o email nao existir, o backend deve criar `Account` automaticamente e publicar `AccountCreatedEvent` com os dados necessarios para o job de criacao do `Owner`.
- Se o email ja existir, o backend deve reutilizar a mesma `Account`, vincular o provedor `google` se ainda nao estiver vinculado e autenticar a sessao sem criar duplicidade.
- O endpoint deve retornar `JwtDto` imediatamente apos sucesso.
- Contas autenticadas por Google devem nascer ou permanecer com `is_verified = true`.
- O `name` vindo do Google deve ser usado como `owner_name` apenas quando o `Owner` precisar ser criado.
- Tentativa de `POST /auth/sign-in` com email/senha para conta sem senha deve retornar erro informativo orientando o uso do Google.

## 3.2 Nao funcionais

- **Seguranca:** o provider deve rejeitar `id_token` invalido, audience divergente, `email` ausente ou `email_verified != true`, retornando erro de autenticacao `401`.
- **Idempotencia:** chamadas repetidas com o mesmo usuario Google nao podem criar `Account` ou vinculos duplicados; publicacao de evento deve acontecer apenas no ramo de criacao da conta.
- **Compatibilidade retroativa:** `POST /auth/sign-up`, `POST /auth/sign-in`, `POST /auth/verify-email` e `POST /auth/resend-verification-email` devem continuar existindo; apenas o tratamento de contas sem senha passa a ter um ramo explicito no login por senha.
- **Resiliencia:** a criacao de `Account`, o vinculo do provedor e a publicacao do evento devem seguir o mesmo padrao transacional ja usado em `src/equiny/rest/controllers/auth/sign_up_account_controller.py`; qualquer falha deve impedir resposta autenticada parcial.

# 4. Regras de Negocio e Invariantes

- O email continua sendo o identificador unico da conta no dominio de auth.
- Uma conta Google nova deve ser persistida com `password = None`, `is_verified = true` e exatamente um vinculo social com `provider = 'google'`.
- Se a conta ja existir e ainda nao possuir vinculo Google, o vinculo deve ser adicionado sem criar outra `Account`.
- Se a conta ja existir e ja possuir vinculo Google, o fluxo deve ser idempotente e apenas emitir novo `JwtDto`.
- A autenticacao via Google de conta nova deve publicar `AccountCreatedEvent`, reutilizando o job atual de criacao de `Owner`.
- A autenticacao via Google nao deve disparar envio de email de verificacao.
- Ao vincular Google a uma conta existente com `Owner` ja criado, o nome atual do `Owner` deve ser preservado; o nome do Google nao deve sobrescrever dados existentes.
- O login por email/senha de conta sem senha nao deve cair em verificacao de hash; deve falhar antes com mensagem orientativa.

# 5. O que ja existe?

## Core

- **`Account`** (`src/equiny/core/auth/domain/entities/account.py`) - entidade de auth que ja modela `social_accounts`, mas hoje ainda assume `password` obrigatoria.
- **`AccountDto`** (`src/equiny/core/auth/domain/entities/dtos/account_dto.py`) - DTO interno usado por entidade e mappers; ja conhece `social_accounts`, mas nao possui default para a lista e ainda assume senha obrigatoria.
- **`SocialAccount`** (`src/equiny/core/auth/domain/structures/social_account.py`) - estrutura de dominio que representa um vinculo social e ja reutiliza `SocialAccountProvider`.
- **`SocialAccountProvider`** (`src/equiny/core/auth/domain/structures/social_account_provider.py`) - enum/value object que ja define `google` como provider valido.
- **`SignUpAccountUseCase`** (`src/equiny/core/auth/use_cases/sign_up_account_use_case.py`) - referencia de criacao de conta por senha e publicacao de evento.
- **`SignInAccountUseCase`** (`src/equiny/core/auth/use_cases/sign_in_account_use_case.py`) - referencia de emissao de `JwtDto` a partir de credenciais locais.
- **`AccountsRepository`** (`src/equiny/core/auth/interfaces/repositories/accounts_repository.py`) - port atual para persistencia de conta, com `add`, `find_by_email`, `find_by_id` e `update`.
- **`AccountCreatedEvent`** (`src/equiny/core/auth/domain/events/account_created_event.py`) - evento de auth ja consumido por `CreateOwnerJob` e que deve ser reutilizado no ramo de criacao por Google.

## Database

- **`AccountModel`** (`src/equiny/database/sqlalchemy/models/auth/account_model.py`) - tabela `accounts` com `email`, `password` e `is_verified`, sem persistencia de provedores sociais.
- **`AccountsMapper`** (`src/equiny/database/sqlalchemy/mappers/auth/accounts_mapper.py`) - mapper atual entre `AccountModel` e `Account`, ainda sem cobrir `social_accounts` e `password = None`.
- **`SqlalchemyAccountsRepository`** (`src/equiny/database/sqlalchemy/repositories/auth/sqlalchemy_accounts_repository.py`) - repositario concreto de `Account` ja integrado ao `DatabasePipe`.
- **`OwnerModel`** (`src/equiny/database/sqlalchemy/models/profiling/owner_model.py`) - tabela `owners` com `account_id` e campos de onboarding.
- **`alembic/versions/5bb89e02f8eb_add_account_and_owner_models.py`** - migration base de `accounts` e `owners`.
- **`alembic/versions/20260301_000000_add_is_verified_to_accounts.py`** - migration que adicionou `accounts.is_verified`.

## REST

- **`SignUpAccountController`** (`src/equiny/rest/controllers/auth/sign_up_account_controller.py`) - referencia de controller fino com `Depends(DatabasePipe, ProvidersPipe, PubSubPipe)`.
- **`SignInAccountController`** (`src/equiny/rest/controllers/auth/sign_in_account_controller.py`) - referencia de endpoint auth que retorna `JwtDto`.
- **`AuthRouter`** (`src/equiny/routers/auth/auth_router.py`) - composition root do modulo `auth`.

## Pipes

- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - ja entrega `AccountsRepository` via `Depends(...)`.
- **`ProvidersPipe`** (`src/equiny/pipes/providers_pipe.py`) - padrao atual para instanciar providers de auth (`HashProvider`, `JwtProvider`, `EmailVerificationProvider`).
- **`PubSubPipe`** (`src/equiny/pipes/pubsub_pipe.py`) - padrao atual para injetar `Broker` no controller.

## Providers / PubSub

- **`JoseJwtProvider`** (`src/equiny/providers/jwt/jose/jose_jwt_provider.py`) - implementacao concreta de emissao de `JwtDto` reutilizavel no novo fluxo.
- **`CreateOwnerJob`** (`src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`) - job atual que consome `AccountCreatedEvent` e deve continuar sendo a fronteira entre auth e profiling.
- **`SendEmailVerificationJob`** (`src/equiny/pubsub/inngest/jobs/notification/send_email_verification_job.py`) - evidencia que o fluxo atual por senha gera verificacao por email, comportamento que deve ser evitado no Google.

# 6. O que deve ser criado?

## Camada Core (Interfaces / Ports)

- **Localizacao:** `src/equiny/core/auth/interfaces/providers/google_auth_provider.py` (**novo arquivo**)
- **Metodos:** `authenticate(id_token: Text) -> tuple[str, str]` - valida o `id_token` do Google contra o audience configurado, garante `email_verified = true` e devolve `(email, name)` para o caso de uso.

## Camada Core (Use Cases)

- **Localizacao:** `src/equiny/core/auth/use_cases/sign_up_with_google_use_case.py` (**novo arquivo**)
- **Dependencias (ports injetados):** `AccountsRepository`, `GoogleAuthProvider`, `JwtProvider`, `Broker`
- **Metodo principal:** `execute(id_token: str) -> JwtDto` - autentica o usuario Google, cria `Text` a partir do token recebido, cria ou vincula a conta, publica evento quando a conta e nova e retorna o JWT da sessao.
- **Fluxo resumido:** validar token Google -> buscar `Account` por email -> criar conta nova ou atualizar conta existente -> publicar `AccountCreatedEvent` apenas na criacao -> persistir alteracoes -> emitir `JwtDto`.

## Camada Database (Models SQLAlchemy)

- **Localizacao:** `src/equiny/database/sqlalchemy/models/auth/social_account_model.py` (**novo arquivo**)
- **Tabela:** `social_accounts`
- **Colunas:** `id` (`String`, PK), `account_id` (`String`, `ForeignKey('accounts.id')`, nao nulo), `email` (`String`, nao nulo), `provider` (`String`, nao nulo)
- **Relacionamentos:** `account: Mapped['AccountModel']` com `back_populates='social_accounts'`
- **Constraints relevantes:** unicidade por `('account_id', 'provider')` e por `('provider', 'email')`

## Camada Database (Mappers)

- **Localizacao:** `src/equiny/database/sqlalchemy/mappers/auth/social_accounts_mapper.py` (**novo arquivo**)
- **Metodos:**
  - `to_entity(model: SocialAccountModel) -> SocialAccount` - converte o registro SQLAlchemy em estrutura de dominio.
  - `to_model(social_account: SocialAccount, account_id: str) -> SocialAccountModel` - monta o model SQLAlchemy para persistencia do vinculo social.

## Camada REST (Controllers)

- **Localizacao:** `src/equiny/rest/controllers/auth/sign_up_with_google_controller.py` (**novo arquivo**)
- **Metodo HTTP e path:** `POST /auth/sign-up/google`
- **`status_code`:** `HTTPStatus.CREATED`
- **`response_model`:** `JwtDto`
- **Dependencias injetadas via `Depends`:** `AccountsRepository`, `GoogleAuthProvider`, `JwtProvider`, `Broker`
- **Fluxo:** `BodySchema` inline no mesmo arquivo, espelhando o padrao de `src/equiny/rest/controllers/auth/sign_in_account_controller.py` -> `SignUpWithGoogleUseCase.execute(body.id_token)` -> resposta `JwtDto`

## Camada Providers

- **Localizacao:** `src/equiny/providers/auth/google/__init__.py` (**novo arquivo**)
- **Responsabilidade:** exportar a implementacao concreta do provider Google para manter o padrao de pacote ja usado em `src/equiny/providers/auth/itsdangerous/__init__.py`.

- **Localizacao:** `src/equiny/providers/auth/google/google_auth_provider.py` (**novo arquivo**)
- **Interface implementada (port):** `GoogleAuthProvider`
- **Biblioteca/SDK utilizado:** `google-auth`
- **Metodos:** `authenticate(id_token: Text) -> tuple[str, str]` - usa `google.oauth2.id_token.verify_oauth2_token(...)`, valida audience com `Env.GOOGLE_OAUTH_CLIENT_ID` e retorna `(email, name)`; levanta `AuthError` para token invalido, audience incorreto ou claims obrigatorias ausentes.

## Migrações Alembic (se aplicavel)

- **Localizacao:** `alembic/versions/` (**novo arquivo**)
- **Operacoes:** criar tabela `social_accounts`; alterar `accounts.password` para `nullable=True`; adicionar constraints e indices necessarios para evitar duplicidade de vinculos sociais.
- **Reversibilidade:** o `downgrade` estrutural e possivel, mas so e seguro se nao existirem contas Google com `password = NULL`; caso existam, o downgrade exige saneamento previo de dados.

# 7. O que deve ser modificado?

## Core

- **Arquivo:** `src/equiny/core/auth/domain/entities/account.py`
- **Mudanca:** permitir `password: Text | None`; manter `social_accounts` como lista de estruturas de dominio mesmo quando vazia.
- **Justificativa:** a PRD exige contas Google sem senha e o dominio ja modela vinculos sociais.

- **Arquivo:** `src/equiny/core/auth/domain/entities/dtos/account_dto.py`
- **Mudanca:** alterar `password` para `str | None` e definir `social_accounts` com lista vazia por padrao.
- **Justificativa:** o DTO precisa representar tanto contas por senha quanto contas Google sem quebrar mappers e casos de uso existentes.

- **Arquivo:** `src/equiny/core/auth/interfaces/providers/__init__.py`
- **Mudanca:** exportar `GoogleAuthProvider`.
- **Justificativa:** alinhar o novo port ao padrao atual de centralizacao de interfaces.

- **Arquivo:** `src/equiny/core/auth/interfaces/repositories/accounts_repository.py`
- **Mudanca:** manter a assinatura de `update(account: Account) -> None`, mas explicitar que a implementacao deve sincronizar `password`, `is_verified` e `social_accounts`.
- **Justificativa:** o fluxo Google precisa atualizar mais de um atributo da conta sem introduzir um port redundante.

- **Arquivo:** `src/equiny/core/auth/use_cases/sign_in_account_use_case.py`
- **Mudanca:** adicionar ramo que detecta `account.password is None` e levanta `AuthError` com mensagem orientando o uso do Google; manter o comportamento atual para contas com senha.
- **Justificativa:** a PRD exige erro informativo para tentativas de login por senha em conta social.

- **Arquivo:** `src/equiny/core/auth/use_cases/sign_up_account_use_case.py`
- **Mudanca:** criar `AccountDto` explicitando `social_accounts=[]` e `password` tipada como opcional, sem alterar o fluxo de verificacao por email.
- **Justificativa:** a evolucao do DTO nao pode quebrar o cadastro existente por senha.

- **Arquivo:** `src/equiny/core/auth/domain/events/account_created_event.py`
- **Mudanca:** permitir payload sem `account_email_verification_token` para o fluxo Google, mantendo `owner_name`, `account_id` e `account_email` como obrigatorios e preservando compatibilidade com o fluxo por senha.
- **Justificativa:** o mesmo evento precisa atender criacao de owner por senha e por Google sem forcar token de verificacao inexistente no cadastro social.

- **Arquivo:** `src/equiny/core/auth/use_cases/__init__.py`
- **Mudanca:** exportar `SignUpWithGoogleUseCase`.
- **Justificativa:** manter consistencia de imports do contexto auth.

## Database

- **Arquivo:** `src/equiny/database/sqlalchemy/models/auth/account_model.py`
- **Mudanca:** tornar `password` anulavel e adicionar relacionamento `social_accounts` com `SocialAccountModel`.
- **Justificativa:** refletir o novo estado de contas Google e persistir provedores sociais de forma normalizada.

- **Arquivo:** `src/equiny/database/sqlalchemy/models/auth/__init__.py`
- **Mudanca:** exportar `SocialAccountModel` alem de `AccountModel`.
- **Justificativa:** seguir a convencao de exports do pacote de models.

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/auth/accounts_mapper.py`
- **Mudanca:** mapear `password = None` corretamente e converter o relacionamento `social_accounts` usando `SocialAccountsMapper`.
- **Justificativa:** a camada database precisa preservar fielmente o contrato do dominio.

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/auth/__init__.py`
- **Mudanca:** exportar `SocialAccountsMapper`.
- **Justificativa:** manter consistencia com os demais pacotes de mappers.

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/auth/sqlalchemy_accounts_repository.py`
- **Mudanca:** atualizar `update(account)` para sincronizar `password`, `is_verified` e a colecao `social_accounts`, preservando idempotencia dos vinculos.
- **Justificativa:** o fluxo Google depende de vinculacao incremental de provider na conta existente.

## REST

- **Arquivo:** `src/equiny/rest/controllers/auth/__init__.py`
- **Mudanca:** exportar `SignUpWithGoogleController`.
- **Justificativa:** permitir registro centralizado do controller no router de auth.

## Routers

- **Arquivo:** `src/equiny/routers/auth/auth_router.py`
- **Mudanca:** registrar `SignUpWithGoogleController.handle(router)` junto aos demais endpoints de auth.
- **Justificativa:** expor o novo endpoint sem alterar a responsabilidade do router como composition root.

## Pipes

- **Arquivo:** `src/equiny/pipes/providers_pipe.py`
- **Mudanca:** adicionar `get_google_auth_provider() -> GoogleAuthProvider`.
- **Justificativa:** manter o controller fino e seguir o padrao atual de DI para providers de auth.

## Providers

- **Arquivo:** `src/equiny/providers/auth/__init__.py`
- **Mudanca:** exportar o provider Google.
- **Justificativa:** manter consistencia com os adaptadores do contexto auth.

## Configuracao / Dependencias

- **Arquivo:** `src/equiny/constants/env.py`
- **Mudanca:** adicionar `GOOGLE_OAUTH_CLIENT_ID: str`.
- **Justificativa:** a validacao do `id_token` precisa de audience explicito, e o usuario confirmou o uso de um unico client ID.

- **Arquivo:** `pyproject.toml`
- **Mudanca:** adicionar dependencia `google-auth`.
- **Justificativa:** o provider concreto precisa usar a biblioteca oficial de validacao de `id_token`.

# 8. O que deve ser removido?

**Nao aplicavel**.

# 9. Decisoes Tecnicas e Trade-offs

## 9.1 Refinamentos consolidados na implementacao

- O provider concreto retorna erro generico `Token Google inválido` para token invalido, audience divergente ou claims obrigatorias ausentes, mantendo a borda HTTP em `401` sem diferenciar causa interna da falha.
- O vinculo de Google em conta local existente preserva a senha atual da conta, apenas marca `is_verified = true` e sincroniza `social_accounts`, permitindo que o login local continue funcional para contas previamente cadastradas com senha.
- O fluxo de criacao de `Owner` permaneceu assincrono e passou a tolerar `account_email_verification_token = None`; nesse caso o job cria o owner, mas nao dispara o envio de email de verificacao.
- A sincronizacao de `social_accounts` no repositorio SQLAlchemy foi consolidada via mapper dedicado para manter a traducao dominio <-> ORM centralizada na camada `database`.

- **Decisao:** manter a criacao de `Owner` via `AccountCreatedEvent` + `CreateOwnerJob`.
- **Alternativas consideradas:** criar `Owner` sincrono no `SignUpWithGoogleUseCase`; acionar `CreateOwnerUseCase` no controller.
- **Motivo da escolha:** respeita a separacao entre os dominios `auth` e `profiling`, evita dependencia de `OwnersRepository` no use case de auth e reaproveita o fluxo ja consolidado no projeto.
- **Impactos / trade-offs:** preserva o desacoplamento arquitetural, mas mantem a janela assincrona existente entre criacao da conta e disponibilidade do `Owner`.

- **Decisao:** persistir provedores sociais em tabela `social_accounts` separada.
- **Alternativas consideradas:** adicionar colunas `provider` em `accounts`; salvar lista em JSON na propria tabela `accounts`.
- **Motivo da escolha:** o dominio ja modela `social_accounts` como colecao, e a tabela separada mantem o schema normalizado e preparado para multi-provider futuro.
- **Impactos / trade-offs:** exige migration extra, relacionamento ORM e sincronizacao de colecao no repository.

- **Decisao:** tornar `accounts.password` anulavel.
- **Alternativas consideradas:** armazenar hash sintetico para contas Google; bloquear social login enquanto `password` continuar obrigatoria.
- **Motivo da escolha:** a PRD pede explicitamente senha nula para contas Google e erro informativo no login por senha.
- **Impactos / trade-offs:** amplia o impacto no dominio, mapper e login por senha, exigindo tratamento explicito de `None`.

- **Decisao:** expor um unico endpoint `POST /auth/sign-up/google` retornando `JwtDto` em todos os cenarios.
- **Alternativas consideradas:** criar dois endpoints (`/sign-up/google` e `/sign-in/google`); criar rota neutra (`/auth/google`).
- **Motivo da escolha:** o nome da tarefa e o padrao atual do modulo auth favorecem um endpoint orientado a acao; o mesmo fluxo atende novo cadastro e login de conta existente.
- **Impactos / trade-offs:** a rota tem semantica mais ampla que o nome sugere, entao a documentacao HTTP deve deixar explicito que a mesma chamada tambem autentica contas ja existentes.

- **Decisao:** validar o token Google com um unico audience (`Env.GOOGLE_OAUTH_CLIENT_ID`).
- **Alternativas consideradas:** aceitar uma lista de audiences por plataforma.
- **Motivo da escolha:** foi a decisao confirmada na fase de levantamento; simplifica o port e a configuracao do backend.
- **Impactos / trade-offs:** a implementacao fica mais simples, mas qualquer expansao futura para multiplos client IDs exigira evolucao do provider e do schema de configuracao.

# 10. Diagramas e Referencias

- **Fluxo de dados:**

```text
HTTP Request
  -> AuthRouter.register()
  -> SignUpWithGoogleController.handle()
  -> Depends(DatabasePipe.get_accounts_repository)
  -> Depends(ProvidersPipe.get_google_auth_provider)
  -> Depends(ProvidersPipe.get_jwt_provider)
  -> Depends(PubSubPipe.get_broker_from_request)
  -> SignUpWithGoogleUseCase.execute(id_token)
       -> GoogleAuthProvider.authenticate(id_token)
       -> AccountsRepository.find_by_email(email)
       -> [account nao existe]
             -> AccountsRepository.add(Account(password=None, is_verified=True, social_accounts=[google]))
             -> Broker.publish(auth/account.created)
          [account existe]
             -> atualizar Account.is_verified / social_accounts se necessario
             -> AccountsRepository.update(account)
       -> JwtProvider.encode(account.id)
  -> Response JSON (`JwtDto`)
```

- **Fluxo assincrono:**

```text
SignUpWithGoogleUseCase
  -> Broker.publish(AccountCreatedEvent)
  -> Inngest / CreateOwnerJob
  -> CreateOwnerUseCase
  -> OwnersRepository.add(owner)
```

- **Referencias:**
  - `src/equiny/rest/controllers/auth/sign_up_account_controller.py`
  - `src/equiny/rest/controllers/auth/sign_in_account_controller.py`
  - `src/equiny/routers/auth/auth_router.py`
  - `src/equiny/core/auth/use_cases/sign_up_account_use_case.py`
  - `src/equiny/core/auth/use_cases/sign_in_account_use_case.py`
  - `src/equiny/core/profiling/use_cases/create_owner_use_case.py`
  - `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`
  - `src/equiny/database/sqlalchemy/repositories/auth/sqlalchemy_accounts_repository.py`
