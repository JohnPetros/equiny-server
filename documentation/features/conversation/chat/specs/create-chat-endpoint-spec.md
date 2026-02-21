---
title: Criar chat no modulo Conversation
prd: documentation/features/conversation/chat/prd.md
status: concluida
last_updated_at: 2026-02-21
---

# 1. Objetivo
Entregar o endpoint `POST /conversation/chats` para criar uma conversa entre dois donos com match, reutilizando `CreateChatUseCase` do contexto `messaging` e usando `VerifyMatchUseCase` dentro de `MatchingPipe.verify_match` (responsavel por disparar `ChatNotAllowedError`), integrando as camadas `rest`, `pipes`, `database/sqlalchemy` e `alembic`, sem acoplamento direto do controller a ORM.

# 2. Escopo

## 2.1 In-scope
- Expor endpoint autenticado `POST /conversation/chats` no novo router de `conversation`.
- Reutilizar e estender `CreateChatUseCase` para validar elegibilidade de chat por match.
- Persistir chats em tabela dedicada (`chats`) com implementacao SQLAlchemy de `ChatsRepository`.
- Validar elegibilidade de match no `MatchingPipe.verify_match(...)` com os dois IDs de cavalo recebidos no body.
- Retornar `ChatDto` como `response_model` do endpoint.

## 2.2 Out-of-scope
- Implementar endpoint de listagem de mensagens (`GET /conversation/chats/{chat_id}/messages`).
- Implementar envio de mensagem (`POST /conversation/chats/{chat_id}/messages`).
- Implementar listagem de chats (`GET /conversation/chats`).
- Implementar exclusao de conversa.

# 3. Requisitos

## 3.1 Funcionais
- Endpoint deve criar chat para o dono autenticado e o outro participante informado indiretamente pelo par de donos no body.
- Body deve obrigatoriamente receber `horse_a_id`, `horse_b_id`, `owner_a_id` e `owner_b_id`.
- Chat so pode ser criado se existir match entre os donos envolvidos.
- `owner_a_id` e `owner_b_id` representam o par de participantes do chat e devem ser persistidos como referencias a `owners` no banco.
- Nao pode existir chat duplicado para o mesmo par de donos.
- Validacao de match deve acontecer via `Depends(MatchingPipe.verify_match)` antes da execucao do `CreateChatUseCase`.
- Quando nao houver match, `MatchingPipe.verify_match` deve disparar `ChatNotAllowedError`.
- Resposta deve ser `HTTPStatus.CREATED` com payload `ChatDto`.

## 3.2 Nao funcionais
- Seguir fluxo `Router -> Controller -> Pipe/Depends -> UseCase -> Repository -> SQLAlchemy`.
- Controller deve permanecer magro (adaptacao HTTP + delegacao).
- Repositorio SQLAlchemy nao deve executar `commit/rollback`.
- Contratos de `core` devem continuar independentes de FastAPI/SQLAlchemy.

# 4. Regras de negocio e invariantes
- Somente donos com match podem abrir chat.
- Cada par de donos deve ter no maximo um chat ativo (independente de quem iniciou).
- Dono autenticado nao pode abrir chat com ele mesmo.
- `owner_a_id` e `owner_b_id` precisam ser `Id` validos, distintos entre si e conter o owner autenticado em um dos lados.
- `horse_a_id` e `horse_b_id` precisam ser `Id` validos e corresponder ao par de cavalos do match.
- A regra de bloqueio por ausencia de match pertence ao `MatchingPipe` (nao ao `CreateChatUseCase`).

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`CreateChatUseCase`** (`src/equiny/core/messaging/use_cases/create_chat_use_case.py`) - ja orquestra criacao de chat e verificacao de duplicidade por `recipient_id` e `sender_id`.
- **`VerifyMatchUseCase`** (`src/equiny/core/matching/use_cases/verify_match_use_case.py`) - valida a existencia de match entre dois cavalos.
- **`ChatDto`** (`src/equiny/core/messaging/domain/entities/dtos/chat_dto.py`) - contrato de entrada/saida para criacao de chat.
- **`ChatsRepository`** (`src/equiny/core/messaging/interfaces/chats_repository.py`) - porta de persistencia da conversa.
- **`ChatAlreadyExistsError`** (`src/equiny/core/messaging/domain/errors/chat_already_exists_error.py`) - erro de conflito ja pronto para duplicidade.

## 5.2 Database (`src/equiny/database/`)
- **`MatchModel`** (`src/equiny/database/sqlalchemy/models/matching/match_model.py`) - tabela de match usada para validar elegibilidade de criacao do chat.
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - contem `owner_id` para relacionar match com dono.
- **`OwnerModel`** (`src/equiny/database/sqlalchemy/models/profiling/owner_model.py`) - tabela de donos que deve ser referenciada por `sender_id` e `recipient_id`.
- **`SqlalchemyRepository`** (`src/equiny/database/sqlalchemy/repositories/sqlalchemy_repository.py`) - base para repositorios SQLAlchemy com `Session`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`SwipeHorseController`** (`src/equiny/rest/controllers/matching/swipe_horse_controller.py`) - referencia de endpoint autenticado com `Depends(AuthPipe.verify_jwt)` + `DatabasePipe`.
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - referencia de endpoint por `IdSchema` em rota aninhada.

## 5.4 Routers (`src/equiny/routers/`)
- **`MatchingRouter`** (`src/equiny/routers/matching/matching_router.py`) - referencia de composicao de modulo com sub-routers.
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - referencia de registro de controllers por recurso.

## 5.5 Validation (`src/equiny/validation/`)
- **`Schema`** (`src/equiny/validation/shared/schema.py`) - base de schemas Pydantic usada no projeto.
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - validacao de ULID para campos de identificador.

## 5.6 Pipes e Middlewares
- **`ProfilingPipe.get_owner_id`** (`src/equiny/pipes/profiling_pipe.py`) - resolve dono autenticado a partir do JWT (`sub`).
- **`AuthPipe.verify_jwt`** (`src/equiny/pipes/auth_pipe.py`) - guard de autenticacao JWT.
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - padrao de injecao de repositorios SQLAlchemy.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - ciclo transacional por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.1 Core

## 6.1.1 Domain (Entities/Structures/Errors/Events)
- **Arquivo:** `src/equiny/core/messaging/domain/errors/chat_not_allowed_error.py` **(novo arquivo)**
  - **Tipo:** `error`
  - **Responsabilidade:** representar violacao da regra "chat so com match" no fluxo de validacao do `MatchingPipe`.
  - **Assinatura/contratos:** `class ChatNotAllowedError(ForbiddenError)`.
  - **Dependencias:** `equiny.core.shared.domain.errors.forbidden_error.ForbiddenError`.
  - **Observacoes:** deve ser disparado por `MatchingPipe.verify_match` quando o par nao for elegivel.

## 6.2 Validation
- **Nao ha novo arquivo previsto.** O `BodySchema` sera declarado no proprio controller.

## 6.3 Database

## 6.3.1 Models
- **Arquivo:** `src/equiny/database/sqlalchemy/models/messaging/chat_model.py` **(novo arquivo)**
  - **Model:** `ChatModel`
  - **Tabela:** `chats`
  - **Campos/indices:** `id`, `owner_a_id`, `owner_b_id`, `created_at`, `updated_at`, com `ForeignKey` para `owners.id` em `owner_a_id` e `owner_b_id`, e indice/constraint para unicidade do par de donos.

- **Arquivo:** `src/equiny/database/sqlalchemy/models/messaging/__init__.py` **(novo arquivo)**
  - **Responsabilidade:** exportar `ChatModel`.

## 6.3.2 Mappers
- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/messaging/chats_mapper.py` **(novo arquivo)**
  - **Mapper:** `ChatsMapper`
  - **Conversao:** `ChatModel <-> Chat`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/messaging/__init__.py` **(novo arquivo)**
  - **Responsabilidade:** exportar `ChatsMapper`.

## 6.3.3 Repositories
- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/messaging/sqlalchemy_chats_repository.py` **(novo arquivo)**
  - **Repository:** `SqlalchemyChatsRepository`
  - **Implementa:** `ChatsRepository`
  - **Metodos:** `add(...)`, `find_by_recipient_id_and_sender_id(...)`, `find_by_id_and_sender_id(...)`, `find_many_by_sender_id(...)`.

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/messaging/__init__.py` **(novo arquivo)**
  - **Responsabilidade:** exportar `SqlalchemyChatsRepository`.

## 6.3.4 Migracoes (Alembic)
- **Mudanca de schema:** criacao da tabela `chats` com relacionamentos para donos e restricao de unicidade do par.
- **Nova migration:** `alembic/versions/<timestamp>_add_chats_table.py` **(novo arquivo)**

## 6.4 Pipes
- **Arquivo:** `src/equiny/pipes/matching_pipe.py` **(novo arquivo)**
  - **Pipe:** `MatchingPipe`
  - **Fornece:** validacao de match via `verify_match`.
  - **Origem:** `DatabasePipe.get_matches_repository` + body com `horse_a_id` e `horse_b_id`.
  - **Semantica de erro:** dispara `ChatNotAllowedError` quando `VerifyMatchUseCase` indicar ausencia de match.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/conversation/create_chat_controller.py` **(novo arquivo)**
  - **Controller:** `CreateChatController`
  - **Rota (relativa):** `/`
  - **`status_code`:** `HTTPStatus.CREATED`
  - **`response_model`:** `ChatDto`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(ProfilingPipe.get_owner_id)`, `Depends(MatchingPipe.verify_match)`, `Depends(DatabasePipe.get_chats_repository)`
  - **Body interno:** `BodySchema` definido no proprio arquivo do controller, com `owner_a_id`, `owner_b_id`, `horse_a_id`, `horse_b_id` e `to_dto() -> ChatDto`.

- **Arquivo:** `src/equiny/rest/controllers/conversation/__init__.py` **(novo arquivo)**
  - **Responsabilidade:** exportar `CreateChatController`.

## 6.6 Routers
- **Arquivo:** `src/equiny/routers/conversation/chats_router.py` **(novo arquivo)**
  - **Router:** `ChatsRouter`
  - **Prefixo:** `/chats`
  - **Controllers:** `CreateChatController.handle(...)`

- **Arquivo:** `src/equiny/routers/conversation/conversation_router.py` **(novo arquivo)**
  - **Router:** `ConversationRouter`
  - **Prefixo:** `/conversation`
  - **Controllers:** composicao via `router.include_router(ChatsRouter.register())`

- **Arquivo:** `src/equiny/routers/conversation/__init__.py` **(novo arquivo)**
  - **Responsabilidade:** exportar `ConversationRouter`.

# 7. O que deve ser modificado

- **Arquivo:** `src/equiny/core/messaging/interfaces/chats_repository.py`
  - **Mudanca:** estender contratos para suportar persistencia com autor autenticado e verificacao de elegibilidade (`add(chat, sender_id)` e `has_match_between_owners(...)`).
  - **Justificativa:** `CreateChatUseCase` precisa persistir o autor do chat e validar regra "so com match".
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/messaging/use_cases/create_chat_use_case.py`
  - **Mudanca:** remover validacao de match da camada de chat e manter apenas verificacao de duplicidade + criacao, propagando `sender_id` para persistencia.
  - **Justificativa:** centralizar regra de elegibilidade no `MatchingPipe` e evitar duplicidade de responsabilidade.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/rest/controllers/conversation/create_chat_controller.py`
  - **Mudanca:** declarar e usar `BodySchema` local no controller (em vez de schema em `validation/conversation`).
  - **Justificativa:** manter o contrato do body encapsulado no endpoint e reduzir dispersao de artefatos de validacao.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/pipes/__init__.py`
  - **Mudanca:** exportar `MatchingPipe` no `__all__`.
  - **Justificativa:** manter API publica da camada de pipes consistente.
  - **Camada:** `pipes/middlewares`

- **Arquivo:** `src/equiny/core/messaging/domain/errors/__init__.py`
  - **Mudanca:** exportar `ChatNotAllowedError`.
  - **Justificativa:** manter API publica do contexto `messaging` consistente.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/messaging/interfaces/__init__.py`
  - **Mudanca:** exportar `ChatsRepository` junto de `MessagesRepository`.
  - **Justificativa:** evitar imports diretos de modulo interno no controller/use case.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/pipes/database_pipe.py`
  - **Mudanca:** adicionar provider `get_chats_repository(...) -> ChatsRepository`.
  - **Justificativa:** manter padrao de DI por `Pipe` na camada REST.
  - **Camada:** `pipes/middlewares`

- **Arquivo:** `src/equiny/app.py`
  - **Mudanca:** registrar `ConversationRouter.register()`.
  - **Justificativa:** expor o novo modulo de rotas no composition root.
  - **Camada:** `routers`

- **Arquivo:** `alembic/env.py`
  - **Mudanca:** importar `ChatModel` para compor `target_metadata`.
  - **Justificativa:** permitir autogenerate/sync de migration da tabela `chats`.
  - **Camada:** `database`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta implementacao.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> ConversationRouter (/conversation)
  -> ChatsRouter (/chats)
  -> CreateChatController (POST /)
  -> Depends(AuthPipe.verify_jwt)
  -> Depends(ProfilingPipe.get_owner_id)
  -> Depends(MatchingPipe.verify_match)
  -> Depends(DatabasePipe.get_chats_repository)
  -> CreateChatUseCase.execute(chat_dto, sender_id)
  -> ChatsRepository.find_by_recipient_id_and_sender_id(recipient_id, sender_id)
  -> ChatsRepository.add(chat, sender_id)
  -> ChatDto (HTTP 201)
```

## 9.2 Referencias internas
- `src/equiny/rest/controllers/matching/swipe_horse_controller.py` (padrao de endpoint autenticado com `Depends`)
- `src/equiny/pipes/profiling_pipe.py` (origem do dono autenticado)
- `src/equiny/core/matching/use_cases/verify_match_use_case.py` (use case reutilizado no `MatchingPipe`)
- `src/equiny/core/messaging/use_cases/create_chat_use_case.py` (use case ja existente a ser estendido)
- `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py` (exemplo de repositorio SQLAlchemy com filtros por par)

# 10. Decisoes finais de implementacao

## 10.1 Ajustes de naming/paths consolidados
- O contexto foi consolidado em `conversation` (nao em `messaging`) para manter consistencia com o modulo e com os endpoints expostos.
- Caminhos finais relevantes:
  - `src/equiny/core/conversation/...`
  - `src/equiny/database/sqlalchemy/{models,mappers,repositories}/conversation/...`
  - `src/equiny/rest/controllers/conversation/...`
  - `src/equiny/routers/conversation/...`

## 10.2 Contrato HTTP final do endpoint de criacao
- Endpoint final: `POST /conversation/chats`.
- Body final implementado no controller:
  - `recipient_id`
  - `sender_id`
  - `recipient_horse_id`
  - `sender_horse_id`
- `MatchingPipe.verify_match` valida elegibilidade via `VerifyMatchUseCase` e dispara `ChatNotAllowedError` quando nao ha match.
- Resposta permanece `HTTP 201` com `ChatDto`.

## 10.3 Persistencia e migracao
- Tabela `chats` criada via migration `alembic/versions/a6e4632d5521_add_chats_table.py`.
- Modelo `ChatModel` usa `owner_a_id` e `owner_b_id` com `ForeignKey` para `owners.id` e indice unico para o par de donos.

## 10.4 Validacao final executada
- `poe codecheck` -> passando.
- `poe typecheck` -> passando.
- `poe test` -> passando (`70 passed`).
