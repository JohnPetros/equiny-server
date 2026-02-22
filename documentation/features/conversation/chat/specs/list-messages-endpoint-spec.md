---
title: Listar mensagens de chat no modulo Conversation
prd: documentation/features/conversation/chat/prd.md
status: concluida
last_updated_at: 2026-02-21
---

# 1. Objetivo
Entregar o endpoint autenticado `GET /conversation/chats/{chat_id}/messages` com paginação por `cursor`, reutilizando o `ListMessagesUseCase` existente e adicionando o adaptador SQLAlchemy de `MessagesRepository`, para percorrer o fluxo completo `Router -> Controller -> Pipe/Depends -> UseCase -> Repository -> SQLAlchemy -> PostgreSQL` sem acoplamento de regra de negocio na camada `rest`.

# 2. Escopo

## 2.1 In-scope
- Expor endpoint `GET /conversation/chats/{chat_id}/messages` no `ChatsRouter`.
- Reutilizar `ListMessagesUseCase` e ajustar seu contrato para `cursor` opcional.
- Implementar persistencia de mensagens no contexto `conversation` com `Model`, `Mapper` e `Repository` SQLAlchemy.
- Retornar payload paginado com `PaginationResponse[MessageDto]` ordenado por mais recentes.
- Integrar DI via `DatabasePipe` para injetar `ChatsRepository` e `MessagesRepository` no controller.

## 2.2 Out-of-scope
- Implementar envio de mensagem via endpoint HTTP (`POST /conversation/chats/{chat_id}/messages`).
- Persistir mensagens recebidas via `WebSocket` (`ChatRoom`) nesta entrega.
- Adicionar status de leitura, contadores de nao lidas ou notificacoes push.
- Alterar contrato de `ChatDto`/listagem de chats para incluir preview de ultima mensagem.

# 3. Requisitos

## 3.1 Funcionais
- Endpoint deve exigir autenticacao JWT de forma indireta via `Depends(ProfilingPipe.get_owner_id)`, que depende de `AuthPipe.verify_jwt`.
- Endpoint deve aceitar `chat_id` na rota e query params `cursor` (opcional) e `limit` (opcional, default `20`, faixa `1..100`).
- Endpoint deve listar apenas mensagens do chat acessado pelo participante autenticado (`sender_id` sendo o `owner_id` resolvido a partir da conta autenticada).
- Resposta deve ser `HTTPStatus.OK` com `PaginationResponse[MessageDto]` contendo `items`, `next_cursor` e `has_more`.
- Mensagens devem ser retornadas em ordem decrescente de envio (mais recente primeiro).
- Ao listar mensagens, mensagens recebidas pelo participante autenticado devem ser marcadas como lidas (`is_read_by_recipient=True`).

## 3.2 Nao funcionais
- Controller deve permanecer fino: adaptar entrada HTTP, instanciar `UseCase` e delegar execucao.
- Repositorio SQLAlchemy nao deve executar `commit`/`rollback`; transacao continua no `HandleSqlalchemySessionMiddleware`.
- Contratos de `core` devem permanecer desacoplados de `FastAPI` e `SQLAlchemy`.
- Consulta paginada deve ter indice para evitar full scan em chats com alto volume de mensagens.

# 4. Regras de negocio e invariantes
- Mensagem pertence obrigatoriamente a um `chat` existente (`chat_id` como `ForeignKey`).
- `sender_id` deve referenciar um dono existente (`ForeignKey` para `owners.id`).
- Apenas participante do chat pode acessar historico (controle por `sender_id` autenticado no fluxo do `UseCase`).
- `cursor` representa o `id` da ultima mensagem da pagina anterior (ULID); sem cursor, retorna primeira pagina.
- `content` pode ser nulo quando a mensagem tiver apenas anexos.
- `attachments` devem ser persistidos em tabela dedicada (`message_attachments`) e mapeados para `AttachmentDto` no dominio.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`ListMessagesUseCase`** (`src/equiny/core/conversation/use_cases/list_messages_use_case.py`) - fluxo base de listagem com validacao de chat e retorno paginado.
- **`MessagesRepository`** (`src/equiny/core/conversation/interfaces/messages_repository.py`) - porta de persistencia para busca e gravacao de mensagens.
- **`Message`** (`src/equiny/core/conversation/domain/entities/message.py`) - entidade de dominio com `content`, `attachments`, `sent_at` e `updated_at`.
- **`MessageDto`** (`src/equiny/core/conversation/domain/entities/dtos/chat_message_dto.py`) - contrato de entrada/saida para mensagens no dominio.
- **`ChatNotFoundError`** (`src/equiny/core/conversation/domain/errors/chat_not_found_error.py`) - erro usado quando chat nao e encontrado para o participante.

## 5.2 Database (`src/equiny/database/`)
- **`ChatModel`** (`src/equiny/database/sqlalchemy/models/conversation/chat_model.py`) - tabela `chats` usada para validar pertencimento do participante.
- **`SqlalchemyChatsRepository`** (`src/equiny/database/sqlalchemy/repositories/conversation/sqlalchemy_chats_repository.py`) - consulta chat por `id` + participante.
- **`SqlalchemyRepository`** (`src/equiny/database/sqlalchemy/repositories/sqlalchemy_repository.py`) - classe base para repositorios com `Session`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`CreateChatController`** (`src/equiny/rest/controllers/conversation/create_chat_controller.py`) - referencia de controller do modulo `conversation` com injecao por `Depends`.
- **`FetchHorseFeedController`** (`src/equiny/rest/controllers/profiling/fetch_horse_feed_controller.py`) - referencia de endpoint paginado com `cursor` e `limit`.

## 5.4 Routers (`src/equiny/routers/`)
- **`ChatsRouter`** (`src/equiny/routers/conversation/chats_router.py`) - sub-router onde o novo endpoint sera registrado.
- **`ConversationRouter`** (`src/equiny/routers/conversation/conversation_router.py`) - router de modulo com prefixo `/conversation`.

## 5.5 Validation (`src/equiny/validation/`)
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - validacao de identificadores ULID em `path/query`.

## 5.6 Pipes e Middlewares
- **`AuthPipe.verify_jwt`** (`src/equiny/pipes/auth_pipe.py`) - resolve e valida payload JWT (origem do `sender_id`).
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - provider de repositorios SQLAlchemy por request.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - ciclo de vida transacional por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.1 Core
- Nenhum novo arquivo previsto no `core` para esta entrega.

## 6.2 Validation
- Nenhum novo arquivo previsto em `validation`; `cursor` e `limit` serao validados no proprio controller com `Query(...)` e `IdSchema`.

## 6.3 Database

## 6.3.1 Models
- **Arquivo:** `src/equiny/database/sqlalchemy/models/conversation/message_model.py` **(novo arquivo)**
  - **Model:** `MessageModel`
  - **Tabela:** `messages`
  - **Campos/indices:** `id` (PK), `chat_id` (`ForeignKey('chats.id')`), `sender_id` (`ForeignKey('owners.id')`), `content` (nullable), `is_read_by_recipient` (default `false`), `sent_at`, `updated_at`; indice composto para paginação (`chat_id`, `id`).

- **Arquivo:** `src/equiny/database/sqlalchemy/models/conversation/attachment_model.py` **(novo arquivo)**
  - **Model:** `AttachmentModel`
  - **Tabela:** `message_attachments`
  - **Campos/indices:** `id` (PK), `message_id` (`ForeignKey('messages.id')`), `key`, `name`, `kind`, `size`; indice por `message_id` para carga eficiente dos anexos.

## 6.3.2 Mappers
- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/conversation/messages_mapper.py` **(novo arquivo)**
  - **Mapper:** `MessagesMapper`
  - **Conversao:** `MessageModel <-> Message` (incluindo mapeamento com `AttachmentModel`).

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/conversation/attachments_mapper.py` **(novo arquivo)**
  - **Mapper:** `AttachmentsMapper`
  - **Conversao:** `AttachmentModel <-> Attachment`.

## 6.3.3 Repositories
- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/conversation/sqlalchemy_messages_repository.py` **(novo arquivo)**
  - **Repository:** `SqlalchemyMessagesRepository`
  - **Implementa:** `MessagesRepository`
  - **Metodos:** `add(...)`, `find_by_chat_id_and_sender_id(...)`, `find_many_by_chat_id_and_sender_id(...)`.

## 6.3.4 Migracoes (Alembic)
 - **Mudanca de schema:** criacao das tabelas `messages` (relacionada a `chats` e `owners`) e `message_attachments` (relacionada a `messages`), com indice de paginação por `chat_id` e indice de relacionamento por `message_id`.
- **Nova migration:** `alembic/versions/20260219_190000_add_messages_and_message_attachments_tables.py` **(novo arquivo)**
- **Nova migration:** `alembic/versions/20260220_120000_add_is_viewed_by_recipient_to_messages.py` **(novo arquivo)**
- **Nova migration:** `alembic/versions/20260222_100000_rename_is_viewed_to_is_read.py` **(novo arquivo - renomeia coluna para `is_read_by_recipient`)**

## 6.4 Pipes
- Nenhum novo arquivo de `Pipe` previsto; a DI sera feita pela extensao do `DatabasePipe` existente.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/conversation/list_messages_controller.py` **(novo arquivo)**
  - **Controller:** `ListMessagesController`
  - **Rota (relativa):** `/{chat_id}/messages`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `PaginationResponse[MessageDto]`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(DatabasePipe.get_chats_repository)`, `Depends(DatabasePipe.get_messages_repository)`

## 6.6 Routers
- Nenhum novo arquivo de router previsto; o endpoint sera registrado no `ChatsRouter` existente.

# 7. O que deve ser modificado

- **Arquivo:** `src/equiny/core/conversation/use_cases/list_messages_use_case.py`
  - **Mudanca:** tornar `cursor` opcional (`str | None`), definir default de `limit` e adaptar conversao para `Id` apenas quando cursor existir.
  - **Justificativa:** alinhar o `UseCase` ao contrato HTTP paginado (primeira pagina sem cursor).
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/conversation/interfaces/messages_repository.py`
  - **Mudanca:** ajustar assinatura de `find_many_by_chat_id_and_sender_id(...)` para receber `cursor: Id | None`.
  - **Justificativa:** manter contrato de repositorio consistente com paginação opcional.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/database/sqlalchemy/models/conversation/__init__.py`
  - **Mudanca:** exportar `MessageModel` e `AttachmentModel` junto de `ChatModel`.
  - **Justificativa:** manter API publica do pacote de models consistente.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/conversation/__init__.py`
  - **Mudanca:** exportar `MessagesMapper` e `AttachmentsMapper` junto de `ChatsMapper`.
  - **Justificativa:** padronizar imports da camada de mappers.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/conversation/__init__.py`
  - **Mudanca:** exportar `SqlalchemyMessagesRepository` junto de `SqlalchemyChatsRepository`.
  - **Justificativa:** padronizar API publica dos repositorios de `conversation`.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/pipes/database_pipe.py`
  - **Mudanca:** adicionar provider `get_messages_repository(...) -> MessagesRepository`.
  - **Justificativa:** manter padrao de DI por `Pipe` e evitar instanciacao manual de repositorio no controller.
  - **Camada:** `pipes/middlewares`

- **Arquivo:** `src/equiny/rest/controllers/conversation/__init__.py`
  - **Mudanca:** exportar `ListMessagesController`.
  - **Justificativa:** preservar padrao de exportacao por pacote de controllers.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/conversation/chats_router.py`
  - **Mudanca:** registrar `ListMessagesController.handle(router)`.
  - **Justificativa:** expor rota de listagem de mensagens no sub-recurso `chats`.
  - **Camada:** `routers`

- **Arquivo:** `alembic/env.py`
  - **Mudanca:** importar `MessageModel` e `AttachmentModel` para compor `target_metadata`.
  - **Justificativa:** garantir deteccao do novo model em migrations.
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
  -> ListMessagesController (GET /{chat_id}/messages)
  -> Depends(AuthPipe.verify_jwt)
  -> Depends(DatabasePipe.get_chats_repository)
  -> Depends(DatabasePipe.get_messages_repository)
  -> ListMessagesUseCase.execute(chat_id, sender_id, cursor, limit)
  -> ChatsRepository.find_by_id_and_sender_id(...)
  -> MessagesRepository.find_many_by_chat_id_and_sender_id(...)
  -> SQLAlchemy (MessageModel/ChatModel)
  -> PostgreSQL
  -> PaginationResponse[MessageDto] (HTTP 200)
```

## 9.2 Referencias internas
- `src/equiny/core/conversation/use_cases/list_messages_use_case.py` (fluxo de listagem ja existente)
- `src/equiny/rest/controllers/profiling/fetch_horse_feed_controller.py` (referencia de paginação por `cursor`/`limit`)
- `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py` (padrao de montagem de `PaginationResponse`)
- `src/equiny/routers/conversation/chats_router.py` (composicao atual de endpoints de chat)
