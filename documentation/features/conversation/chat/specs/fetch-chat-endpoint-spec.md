---
title: Buscar chat por ID no modulo Conversation
prd: documentation/features/conversation/chat/prd.md
status: em progresso
last_updated_at: 2026-02-19
---

# 1. Objetivo
Entregar o endpoint autenticado `GET /conversation/chats/{chat_id}` para retornar os dados de uma conversa especifica (`ChatDto`) somente quando o usuario autenticado for participante do chat, reutilizando `GetChatUseCase` e a validacao de acesso via `ConversationPipe.verify_chat_participant`, mantendo o fluxo padrao `HTTP -> Router -> Controller -> Pipe/Depends -> UseCase -> Repository -> SQLAlchemy -> PostgreSQL`.

# 2. Escopo

## 2.1 In-scope
- Criar controller REST para busca de chat por `chat_id`.
- Registrar endpoint no `ChatsRouter` existente.
- Reutilizar `GetChatUseCase` para leitura do chat no `core`.
- Reutilizar `ConversationPipe.verify_chat_participant` como guard de autorizacao por participacao.
- Retornar `HTTPStatus.OK` com `response_model=ChatDto`.

## 2.2 Out-of-scope
- Alteracoes em criacao de chat (`POST /conversation/chats`).
- Alteracoes em listagem de mensagens (`GET /conversation/chats/{chat_id}/messages`).
- Alteracoes em modelos, mappers, repositorios SQLAlchemy ou migrations.
- Mudancas no contrato de `ChatDto` (campos, forma de serializacao).

# 3. Requisitos

## 3.1 Funcionais
- Endpoint deve aceitar `chat_id` no path (`IdSchema`/ULID valido).
- Endpoint deve resolver `owner_id` autenticado via `Depends(ProfilingPipe.get_owner_id)`.
- Endpoint deve validar autorizacao de acesso ao chat via `Depends(ConversationPipe.verify_chat_participant)`.
- Endpoint deve buscar chat com `GetChatUseCase.execute(chat_id, sender_id)`.
- `sender_id` deve ser o `owner_id` autenticado (nao `account_id` do JWT) para manter consistencia com `ChatsRepository`.
- Em sucesso, deve retornar `ChatDto` com `HTTPStatus.OK`.
- Se o chat nao existir para o participante autenticado, deve retornar erro de dominio mapeado para `404` (`ChatNotFoundError`).
- Se o usuario autenticado nao for participante do chat, deve retornar erro mapeado para `403` (`ChatNotAllowedError`, disparado no pipe).

## 3.2 Nao funcionais
- Controller deve permanecer magro: adaptar entrada HTTP e delegar ao `UseCase`.
- Nao deve haver regra de negocio nova na camada `rest`.
- Nao deve haver controle de transacao no controller/repository (ciclo no middleware de sessao).
- Reutilizar componentes existentes, sem duplicar `UseCase`, `Pipe`, `DTO` ou `Repository`.

# 4. Regras de negocio e invariantes
- Apenas participantes de um chat podem consultar os dados da conversa.
- `chat_id` deve ser um identificador valido no formato ULID.
- A verificacao de permissao de participante acontece antes da execucao do `GetChatUseCase`.
- O repositorio deve filtrar por `chat_id` e participante para evitar vazamento de dados entre donos.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`GetChatUseCase`** (`src/equiny/core/conversation/use_cases/get_chat_use_case.py`) - use case pronto para buscar chat por `chat_id` + `sender_id` e lançar `ChatNotFoundError`.
- **`ChatsRepository`** (`src/equiny/core/conversation/interfaces/chats_repository.py`) - contrato ja contem `find_by_id_and_sender_id(...)` e `find_by_id_and_participant_id(...)`.
- **`ChatDto`** (`src/equiny/core/conversation/domain/entities/dtos/chat_dto.py`) - contrato de saida do endpoint.
- **`ChatNotFoundError`** (`src/equiny/core/conversation/domain/errors/chat_not_found_error.py`) - erro de ausencia do chat para o participante.
- **`ChatNotAllowedError`** (`src/equiny/core/conversation/domain/errors/chat_not_allowed_error.py`) - erro de autorizacao por nao participacao.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyChatsRepository`** (`src/equiny/database/sqlalchemy/repositories/conversation/sqlalchemy_chats_repository.py`) - implementacao concreta para leitura de chats por participante.
- **`ChatModel`** (`src/equiny/database/sqlalchemy/models/conversation/chat_model.py`) - tabela de persistencia de chats com relacao de participantes.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`CreateChatController`** (`src/equiny/rest/controllers/conversation/create_chat_controller.py`) - referencia de controller no modulo `conversation`.
- **`ListMessagesController`** (`src/equiny/rest/controllers/conversation/list_messages_controller.py`) - referencia de endpoint autenticado no mesmo recurso (`/chats`).

## 5.4 Routers (`src/equiny/routers/`)
- **`ChatsRouter`** (`src/equiny/routers/conversation/chats_router.py`) - sub-router onde o novo endpoint deve ser registrado.
- **`ConversationRouter`** (`src/equiny/routers/conversation/conversation_router.py`) - modulo com prefixo `/conversation`.

## 5.5 Validation (`src/equiny/validation/`)
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - validacao de ULID para parametro de rota.

## 5.6 Pipes e Middlewares
- **`ConversationPipe.verify_chat_participant`** (`src/equiny/pipes/conversation_pipe.py`) - verifica se o owner autenticado participa do chat.
- **`AuthPipe.verify_jwt`** (`src/equiny/pipes/auth_pipe.py`) - validacao base de JWT, acionada pelo `ProfilingPipe`.
- **`ProfilingPipe.get_owner_id`** (`src/equiny/pipes/profiling_pipe.py`) - resolve `owner_id` autenticado (valor usado como `sender_id` no `GetChatUseCase`).
- **`DatabasePipe.get_chats_repository`** (`src/equiny/pipes/database_pipe.py`) - provider de repositorio SQLAlchemy de chat.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - ciclo transacional por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/conversation/fetch_chat_controller.py` **(novo arquivo)**
  - **Controller:** `FetchChatController`
  - **Rota (relativa):** `/{chat_id}`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `ChatDto`
  - **Dependencias:** `Depends(ProfilingPipe.get_owner_id)`, `Depends(ConversationPipe.verify_chat_participant)`, `Depends(DatabasePipe.get_chats_repository)`
  - **Fluxo interno:** recebe `chat_id`, recebe `owner_id` autenticado, instancia `GetChatUseCase` e retorna `use_case.execute(chat_id, owner_id.value)`.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/rest/controllers/conversation/__init__.py`
  - **Mudanca:** exportar `FetchChatController` no pacote.
  - **Justificativa:** manter padrao de API publica dos controllers do modulo `conversation`.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/conversation/chats_router.py`
  - **Mudanca:** registrar `FetchChatController.handle(router)`.
  - **Justificativa:** expor endpoint `GET /conversation/chats/{chat_id}` dentro do recurso de chats.
  - **Camada:** `routers`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta implementacao.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> ConversationRouter (/conversation)
  -> ChatsRouter (/chats)
  -> FetchChatController (GET /{chat_id})
  -> Depends(ProfilingPipe.get_owner_id)
  -> Depends(ConversationPipe.verify_chat_participant)
  -> Depends(DatabasePipe.get_chats_repository)
  -> GetChatUseCase.execute(chat_id, sender_id)
  -> ChatsRepository.find_by_id_and_sender_id(...)
  -> SQLAlchemy (ChatModel)
  -> PostgreSQL
  -> ChatDto (HTTP 200)
```

## 9.2 Referencias internas
- `src/equiny/core/conversation/use_cases/get_chat_use_case.py` (busca de chat por participante)
- `src/equiny/pipes/conversation_pipe.py` (guard de autorizacao por participacao)
- `src/equiny/database/sqlalchemy/repositories/conversation/sqlalchemy_chats_repository.py` (query de chat por `chat_id` e participante)
- `src/equiny/rest/controllers/conversation/list_messages_controller.py` (referencia de endpoint autenticado no mesmo modulo)
- `src/equiny/routers/conversation/chats_router.py` (composicao do recurso `chats`)
