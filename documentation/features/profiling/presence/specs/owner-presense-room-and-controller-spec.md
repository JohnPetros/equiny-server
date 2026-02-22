---
title: Presenca de owner por WebSocket e endpoint de consulta
prd: https://raw.githubusercontent.com/JohnPetros/equiny/refs/heads/main/documentation/overview.md
status: concluida
last_updated_at: 2026-02-22
---

# 1. Objetivo
Entregar o fluxo de presenca de `owners` no contexto `profiling`, com uma `WebSocket room` que registra/desregistra presenca em cache (`Redis`) e um endpoint HTTP `GET /profiling/owners/{owner_id}/presence` para consultar status online por owner. A entrega deve manter o fluxo arquitetural `HTTP` -> `Router` -> `Controller` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL` para validacao de owner, e `WebSocket` -> `Room` -> `Pipe/Depends` -> `UseCase` -> `CacheProvider` para atualizacao de presenca. **Risco principal:** inconsistencias atuais de naming (`presense`) e room incompleta podem bloquear a execucao se nao forem corrigidas junto.

# 2. Escopo

## 2.1 In-scope
- Implementar provider de cache `Redis` aderente a `CacheProvider`.
- Adicionar infraestrutura local de `Redis` no `docker-compose` e configuracao de `ENV`.
- Finalizar `OwnersPresenceRoom` para: autenticar por JWT em query, resolver owner autenticado via `OwnersRepository.find_by_account_id`, registrar presenca no cache e emitir broadcast.
- Criar endpoint HTTP para consultar presenca de um owner por `owner_id` em path.
- Criar `UseCase` dedicado para consulta de presenca e estruturar retorno tipado.
- Registrar `Room` e `Controller` no `OwnersRouter` do modulo `profiling`.

## 2.2 Out-of-scope
- Implementar listagem em lote de presenca (`bulk`) para varios owners.
- Alterar regras de chat/match para depender de presenca em tempo real.
- Criar dashboard de monitoramento de conexoes WebSocket.
- Refactor amplo de nomenclaturas legadas (`presense`, `onwer`, `horsers`) fora dos pontos tocados por esta feature.

# 3. Requisitos

## 3.1 Funcionais
- O sistema deve expor `WebSocket /profiling/owners/{owner_id}/presence` para conexao de presenca.
- A conexao WebSocket deve exigir token JWT por query (`token`) e derivar o owner autenticado via `OwnersRepository.find_by_account_id`.
- O `owner_id` da rota WebSocket deve ser consistente com o owner do JWT; divergencia deve encerrar conexao com erro de autorizacao.
- Ao conectar, o fluxo deve executar `RegisterOwnerPresenceUseCase` e enviar broadcast com o `owner_id` conectado.
- Ao desconectar, o fluxo deve executar `UnregisterOwnerPresenceUseCase` e remover a chave de presenca no cache.
- O endpoint `GET /profiling/owners/{owner_id}/presence` deve retornar status online baseado no cache, validando existencia do owner no repositorio.

## 3.2 Nao funcionais
- `Controller` deve permanecer fino: adaptar entrada HTTP e delegar ao `UseCase`.
- `Room` nao deve conter regra de negocio complexa; deve apenas orquestrar conexoes/dependencias e chamar `UseCases`.
- `CacheProvider` deve encapsular SDK de `Redis` e manter contrato simples `get/set/delete`.
- Nao executar `commit/rollback` manual em repositorios SQLAlchemy; ciclo transacional permanece no middleware HTTP e no `Sqlalchemy.session()` para WebSocket.
- Broadcast deve usar payload serializavel (dataclass/DTO) para compatibilidade com `Ws.broadcast`.

# 4. Regras de negocio e invariantes
- Presenca online e determinada pela existencia da chave `profiling:owners:presence:{owner_id}` no cache.
- Apenas owners existentes podem ser marcados/desmarcados como presentes.
- Conexao WebSocket autenticada nao pode publicar presenca de outro owner.
- Endpoint HTTP de consulta de presenca deve retornar `404` quando owner nao existir.
- Broadcast de entrada deve carregar ao menos `owner_id` e estado de presenca atual (`is_online`).

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`CacheProvider`** (`src/equiny/core/shared/interfaces/cache_provider.py`) - contrato de cache com `get/set/delete`.
- **`RegisterOwnerPresenceUseCase`** (`src/equiny/core/profiling/use_cases/register_owner_presense_use_case.py`) - registra presenca do owner no cache com `CACHE_KEYS.OWNERS_PRESENCE`.
- **`UnregisterOwnerPresenceUseCase`** (`src/equiny/core/profiling/use_cases/unregister_owner_presence_use_case.py`) - remove presenca do cache no disconnect.
- **`OwnersRepository`** (`src/equiny/core/profiling/interfaces/repositories/owners_repository.py`) - contrato para validar existencia de owner por `id`/`account_id`.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyOwnersRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_owners_repository.py`) - implementacao concreta do repositorio de owners.
- **`OwnerModel`** (`src/equiny/database/sqlalchemy/models/profiling/owner_model.py`) - tabela `owners` usada para validar owner autenticado; recebera persistencia de `last_presence_at`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`FetchOwnerController`** (`src/equiny/rest/controllers/profiling/fetch_onwer_controller.py`) - referencia de endpoint de leitura no contexto `owners`.

## 5.4 Routers (`src/equiny/routers/`)
- **`OwnersRouter`** (`src/equiny/routers/profiling/owners_router.py`) - composicao das rotas de `owners` sob `/profiling/owners`.

## 5.5 Validation (`src/equiny/validation/`)
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - validacao de `owner_id` no path.

## 5.6 Pipes e Middlewares
- **`AuthPipe.verify_jwt_from_query`** (`src/equiny/pipes/auth_pipe.py`) - dependencia para JWT em conexao WebSocket.
- **`ProvidersPipe`** (`src/equiny/pipes/providers_pipe.py`) - fabrica de providers; ainda sem provider de cache.
- **`Ws`** (`src/equiny/websocket/rooms/ws.py`) - utilitario para `connect`, `disconnect` e `broadcast`.
- **`OwnersPresenceRoom`** (`src/equiny/websocket/rooms/profiling/owners_presence_room.py`) - estrutura inicial da room (ainda incompleta).

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.1 Core

## 6.1.1 Domain (Entities/Structures/Errors/Events)
- **Arquivo:** `src/equiny/core/profiling/domain/structures/dtos/owner_presence_dto.py` **(novo arquivo)**
  - **Tipo:** `structure`
  - **Responsabilidade:** contrato de saida para status de presenca.
  - **Assinatura/contratos:** `OwnerPresenceDto(owner_id: str, is_online: bool)`.
  - **Dependencias:** `equiny.core.shared.domain.decorators.dto`.
  - **Observacoes:** DTO deve ser serializavel para `response_model` e broadcast.

## 6.1.3 Use Cases
- **Arquivo:** `src/equiny/core/profiling/use_cases/get_owner_presence_use_case.py` **(novo arquivo)**
  - **Use case:** `GetOwnerPresenceUseCase`
  - **Entrada:** `owner_id: str`
  - **Saida:** `OwnerPresenceDto`
  - **Dependencias:** `OwnersRepository`, `CacheProvider`
  - **Fluxo:** validar owner existe -> consultar chave de cache -> montar `OwnerPresenceDto`.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/profiling/fetch_owner_presence_controller.py` **(novo arquivo)**
  - **Controller:** `FetchOwnerPresenceController`
  - **Rota (relativa):** `/{owner_id}/presence`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `OwnerPresenceDto`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(DatabasePipe.get_owners_repository)`, `Depends(ProvidersPipe.get_cache_provider)`.

## 6.7 Providers e Infra
- **Arquivo:** `src/equiny/providers/cache/redis/redis_cache_provider.py` **(novo arquivo)**
  - **Tipo:** provider de infraestrutura.
  - **Responsabilidade:** implementar `CacheProvider` usando cliente `redis` com URL de `ENV.REDIS_URL`.
  - **Assinatura/contratos:** `class RedisCacheProvider(CacheProvider)` com `get/set/delete`.
  - **Dependencias:** `redis`, `equiny.constants.ENV`, `equiny.core.shared.interfaces.cache_provider.CacheProvider`.

- **Arquivo:** `src/equiny/providers/cache/__init__.py` **(novo arquivo)**
  - **Responsabilidade:** exportar provider de cache do pacote.

- **Arquivo:** `src/equiny/providers/cache/redis/__init__.py` **(novo arquivo)**
  - **Responsabilidade:** exportar `RedisCacheProvider`.

- **Arquivo:** `src/equiny/websocket/rooms/profiling/__init__.py` **(novo arquivo)**
  - **Responsabilidade:** exportar `OwnersPresenceRoom` para facilitar import no router.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/core/profiling/domain/structures/owner_presence.py`
  - **Mudanca:** definir estrutura de dominio `OwnerPresence` com conversao para `OwnerPresenceDto`.
  - **Justificativa:** arquivo existe vazio e precisa ser o objeto de dominio da feature.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/profiling/domain/structures/dtos/__init__.py`
  - **Mudanca:** exportar `OwnerPresenceDto` em `__all__`.
  - **Justificativa:** manter API publica do contexto `profiling` consistente.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/profiling/domain/structures/__init__.py`
  - **Mudanca:** exportar `OwnerPresence`.
  - **Justificativa:** permitir imports estaveis nas camadas `rest` e `websocket`.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/profiling/use_cases/__init__.py`
  - **Mudanca:** exportar `GetOwnerPresenceUseCase`.
  - **Justificativa:** padronizar barrel export dos use cases.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/pipes/providers_pipe.py`
  - **Mudanca:** adicionar `get_cache_provider() -> CacheProvider` retornando `RedisCacheProvider`.
  - **Justificativa:** centralizar DI de provider de cache no mesmo padrao dos demais providers.
  - **Camada:** `pipes/middlewares`

- **Arquivo:** `src/equiny/websocket/rooms/profiling/owners_presence_room.py`
  - **Mudanca:** implementar fluxo completo da room (`async`, auth por query, validacao `owner_id` path vs JWT, register/unregister, broadcast).
  - **Justificativa:** arquivo atual e apenas stub e nao registra presenca real.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** exportar `FetchOwnerPresenceController`.
  - **Justificativa:** manter composicao por pacote no padrao atual.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/owners_router.py`
  - **Mudanca:** registrar `FetchOwnerPresenceController.handle(router)` e `OwnersPresenceRoom.handle(router)`.
  - **Justificativa:** expor endpoint HTTP e room WebSocket no contexto `/profiling/owners`.
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/database/sqlalchemy/models/profiling/owner_model.py`
  - **Mudanca:** adicionar coluna `last_presence_at` (`datetime`, nullable).
  - **Justificativa:** persistir ultimo timestamp de presenca/saida do owner, alinhado com `Owner.last_presence_at` no dominio.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/owners_mapper.py`
  - **Mudanca:** mapear `last_presence_at` em `to_dto(...)` e `to_model(...)`.
  - **Justificativa:** manter consistencia de conversao entre entidade de dominio e ORM.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_owners_repository.py`
  - **Mudanca:** incluir persistencia de `last_presence_at` no metodo `replace(...)`.
  - **Justificativa:** garantir que `UnregisterOwnerPresenceUseCase` reflita o timestamp no banco.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/constants/env.py`
  - **Mudanca:** adicionar `REDIS_URL` em `Env`.
  - **Justificativa:** externalizar configuracao do cache provider.
  - **Camada:** `core`

- **Arquivo:** `.env.example`
  - **Mudanca:** incluir `REDIS_URL=`.
  - **Justificativa:** onboarding local da nova dependencia de infraestrutura.
  - **Camada:** `core`

- **Arquivo:** `pyproject.toml`
  - **Mudanca:** adicionar dependencia `redis`.
  - **Justificativa:** suporte ao provider de cache Redis.
  - **Camada:** `core`

- **Arquivo:** `docker-compose.yml`
  - **Mudanca:** adicionar servico `redis` (ex.: `redis:7-alpine`) para ambiente local.
  - **Justificativa:** requisito explicito da feature para cache provider com Redis.
  - **Camada:** `database`

- **Arquivo:** `alembic/versions/<...>.py` **(novo arquivo)**
  - **Mudanca:** migration para adicionar coluna `last_presence_at` em `owners`.
  - **Justificativa:** versionar alteracao de schema conforme regras de banco.
  - **Camada:** `database`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta implementacao.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
HTTP Client
  -> GET /profiling/owners/{owner_id}/presence
  -> ProfilingRouter (/profiling)
  -> OwnersRouter (/owners)
  -> FetchOwnerPresenceController
  -> Depends(AuthPipe.verify_jwt)
  -> Depends(DatabasePipe.get_owners_repository)
  -> Depends(ProvidersPipe.get_cache_provider)
  -> GetOwnerPresenceUseCase
  -> OwnersRepository.find_by_id + CacheProvider.get
  -> PostgreSQL + Redis
  <- OwnerPresenceDto (HTTP 200)

WebSocket Client
  -> WS /profiling/owners/{owner_id}/presence?token=<jwt>
  -> OwnersPresenceRoom
  -> Depends(AuthPipe.verify_jwt_from_query)
  -> RegisterOwnerPresenceUseCase / UnregisterOwnerPresenceUseCase
  -> CacheProvider.set/delete
  -> Ws.broadcast(OwnerPresenceDto)
```

## 9.2 Referencias internas
- `src/equiny/websocket/rooms/conversation/chat_room.py` (exemplo de composicao de room em router)
- `src/equiny/rest/controllers/profiling/fetch_onwer_controller.py` (padrao de controller no contexto `owners`)
- `src/equiny/core/profiling/use_cases/register_owner_presense_use_case.py` (registro de presenca no cache)
- `src/equiny/core/profiling/use_cases/unregister_owner_presence_use_case.py` (limpeza de presenca no disconnect)
- `src/equiny/pipes/profiling_pipe.py` (resolucao de owner autenticado)

# 10. Decisoes de implementacao

- `OwnerPresenceDto` foi consolidado como `owner_id` + `is_online` para uso uniforme em HTTP e WebSocket broadcast.
- A room foi registrada em `/profiling/owners/{owner_id}/presence` via `OwnersRouter`, mantendo path relativo `/{owner_id}/presence`.
- O fluxo de disconnect publica broadcast de `is_online=False` apenas quando o owner chegou a ser registrado com sucesso na sessao atual.
