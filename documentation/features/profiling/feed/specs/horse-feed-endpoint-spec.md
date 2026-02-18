---
title: Endpoint de feed de cavalos
status: concluido
last_updated_at: 2026-02-17
---

# 1. Objetivo
Entregar o endpoint autenticado `GET /profiling/horses/{horse_id}/feed` para listar cavalos elegiveis no feed com filtros de descoberta e paginacao por cursor, reutilizando `GetHorseFeedUseCase` e fechando o fluxo `HTTP` -> `Router` -> `Controller` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL`, sem introduzir regra de negocio na borda REST.

# 2. Escopo

## 2.1 In-scope
- Expor rota `GET /profiling/horses/{horse_id}/feed` no contexto `profiling/horses`.
- Exigir autenticacao via `Depends(AuthPipe.verify_jwt)`.
- Receber filtros de feed por `query params` via `QuerySchema` e converter para tipos de dominio (`AgeRangeDto`, `LocationDto`).
- Reutilizar `GetHorseFeedUseCase` existente como orquestrador da busca.
- Implementar `find_many(...)` em `SqlalchemyHorsesRepository` para filtros e paginacao.
- Registrar controller no `HorsesRouter` e exportar novos contratos em `__init__.py` necessarios.
- Corrigir o tratamento de `cursor` no use case para nao gerar `Id` aleatorio quando `cursor` nao for informado.

## 2.2 Out-of-scope
- Alteracao de schema de banco e criacao de migration Alembic.
- Mudancas no fluxo de `swipe`, `match` ou chat.
- Regras avancadas de ranking/ordenacao por relevancia (ex.: score, boost, machine learning).
- Refactor amplo de nomenclaturas legadas (`horsers`, `onwer`, etc.) fora do necessario para o endpoint.

# 3. Requisitos

## 3.1 Funcionais
- O endpoint deve receber `horse_id` no path para identificar o cavalo de contexto do feed.
- O endpoint deve aceitar filtros de descoberta por `query params`: `sex`, `height`, `breeds`, `min_age`, `max_age`, `city`, `state`, `cursor` (opcional) e `limit` (opcional).
- O endpoint deve retornar `PaginationResponse[HorseDto]` com `items`, `next_cursor` e `has_more`.
- O endpoint deve retornar apenas cavalos `is_active = true`.
- O endpoint deve aplicar filtros de sexo, faixa etaria, altura maxima, raca(s) e localizacao.
- O endpoint deve ordenar por criterio estavel para paginacao por cursor (mais recentes primeiro).
- O endpoint deve respeitar `limit` com limite padrao (ex.: `20`) e estrategia `limit + 1` para calcular `has_more`.

## 3.2 Nao funcionais
- `Controller` deve permanecer magro: validar/adaptar/delegar.
- `UseCase` deve continuar sem dependencia de `FastAPI`/`SQLAlchemy`.
- Repositorio nao deve executar `commit`/`rollback` manual.
- Contrato de `HorsesRepository` deve ser mantido coeso com assinatura de `GetHorseFeedUseCase`.
- Implementacao deve seguir padrao de composicao por `Router` + `Controller.handle(...)`.

# 4. Regras de negocio e invariantes
- **Apenas perfis ativos:** cavalos inativos nao aparecem no feed.
- **Filtro de compatibilidade:** feed deve aplicar `sex` recebido na busca (MVP: compatibilidade por sexo).
- **Filtro por idade:** idade deve respeitar intervalo valido e `max_age >= min_age`.
- **Filtro por localizacao:** resultado deve restringir por `city` e `state` informados.
- **Paginacao deterministica:** `next_cursor` deve apontar para o ultimo item da pagina retornada.
- **Sem regra de dominio no controller:** validacao de negocio permanece no `core`/estruturas.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`GetHorseFeedUseCase`** (`src/equiny/core/profiling/use_cases/get_horse_feed_use_case.py`) - caso de uso ja existente para descoberta, aguardando integracao completa com endpoint/repositorio.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - contrato de persistencia com metodo `find_many(...)` ja declarado.
- **`AgeRange` / `AgeRangeDto`** (`src/equiny/core/profiling/domain/structures/age_range.py`, `src/equiny/core/profiling/domain/structures/dtos/age_range_dto.py`) - regra e contrato para faixa etaria.
- **`Location` / `LocationDto`** (`src/equiny/core/profiling/domain/structures/location.py`, `src/equiny/core/profiling/domain/structures/dtos/location_dto.py`) - regra e contrato para localizacao.
- **`PaginationResponse`** (`src/equiny/core/shared/responses/pagination_response.py`) - contrato padrao de resposta paginada.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - repositorio concreto de cavalos; ainda sem implementacao de `find_many(...)`.
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - modelo ORM da tabela `horses` com colunas necessarias para filtros.
- **`HorsesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`) - conversao entre `HorseModel` e `Horse`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - referencia de endpoint `GET` com `Depends` e retorno `HorseDto`.
- **`ListMatchesController`** (`src/equiny/rest/controllers/matching/list_matches_controller.py`) - referencia de endpoint com `PaginationResponse` e `cursor`.

## 5.4 Routers (`src/equiny/routers/`)
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - ponto de composicao para endpoints de `horses`.
- **`ProfilingRouter`** (`src/equiny/routers/profiling/profiling_router.py`) - inclui `HorsesRouter` sob `prefix='/profiling'`.

## 5.5 Validation (`src/equiny/validation/`)
- **`HorseSchema`** (`src/equiny/validation/profiling/horse_schema.py`) - referencia de padrao de schema com `to_dto()` no contexto `profiling`.
- **`LocationSchema`** (`src/equiny/validation/profiling/location_schema.py`) - schema reutilizavel para localizacao.
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - tipo reutilizavel para UUID na borda.

## 5.6 Pipes e Middlewares
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - entrega `HorsesRepository` por request.
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - guard de autenticacao JWT para endpoint protegido.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - ciclo transacional da sessao SQLAlchemy por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma secao nao esteja envolvida na implementacao, ignore-a na spec.

## 6.2 Validation
- Nenhum novo arquivo em `src/equiny/validation/`.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/profiling/fetch_horse_feed_controller.py` (**novo arquivo**)
  - **Controller:** `FetchHorseFeedController`
  - **Rota (relativa):** `/{horse_id}/feed`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `PaginationResponse[HorseDto]`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(DatabasePipe.get_horses_repository)`
  - **QuerySchema (local no controller):** `FeedHorsesSchema`
  - **Campos de query:** `sex`, `height`, `breeds`, `min_age`, `max_age`, `city`, `state`, `cursor`, `limit`
  - **Observacoes:** `FeedHorsesSchema` deve ser definido no proprio arquivo do controller e usado como schema de query, com `to_dto()` para adaptar entrada ao `GetHorseFeedUseCase`.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/core/profiling/use_cases/get_horse_feed_use_case.py`
  - **Mudanca:** ajustar `execute(...)` para tratar `cursor` opcional corretamente (`None` nao deve virar `Id` novo) e receber `limit` com default.
  - **Justificativa:** evitar pagina vazia/instavel na primeira chamada e padronizar paginacao.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`
  - **Mudanca:** estender assinatura de `find_many(...)` com `limit: int = 20` e cursor opcional coerente com estrategia de paginacao.
  - **Justificativa:** alinhar contrato de dominio com necessidade do endpoint e implementacao SQLAlchemy.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
  - **Mudanca:** implementar `find_many(...)` com filtros (`sex`, `age_range`, `height`, `breeds`, `location`, `is_active`) e paginacao por cursor.
  - **Justificativa:** completar adaptador de persistencia exigido por `GetHorseFeedUseCase`.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** exportar `FetchHorseFeedController` em `__all__`.
  - **Justificativa:** manter barrel export estavel para registro em router.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/horses_router.py`
  - **Mudanca:** registrar `FetchHorseFeedController.handle(router)`.
  - **Justificativa:** expor endpoint no modulo `profiling/horses`.
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/validation/profiling/__init__.py`
  - **Mudanca:** nenhuma.
  - **Justificativa:** `FeedHorsesSchema` sera `QuerySchema` local do controller, sem novo artefato no pacote `validation`.
  - **Camada:** `validation`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> GET /profiling/horses/{horse_id}/feed
     Query: ?sex=...&height=...&breeds=...&min_age=...&max_age=...&city=...&state=...&cursor=...&limit=...
  -> ProfilingRouter (/profiling)
  -> HorsesRouter (/horses)
  -> FetchHorseFeedController (/{horse_id}/feed)
       -> Depends(AuthPipe.verify_jwt)
       -> Depends(DatabasePipe.get_horses_repository)
       -> QuerySchema local: FeedHorsesSchema
  -> GetHorseFeedUseCase.execute(...)
  -> HorsesRepository.find_many(...)
  -> SqlalchemyHorsesRepository (SQLAlchemy query + pagination)
  -> PostgreSQL (horses)
  <- PaginationResponse[HorseDto]
```

## 9.2 Referencias internas
- `src/equiny/core/profiling/use_cases/get_horse_feed_use_case.py` (caso de uso alvo)
- `src/equiny/core/profiling/interfaces/repositories/horsers_repository.py` (contrato de persistencia)
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py` (repositorio alvo da implementacao)
- `src/equiny/rest/controllers/matching/list_matches_controller.py` (referencia de paginacao no REST)
- `src/equiny/routers/profiling/horses_router.py` (composicao de endpoints do modulo)
