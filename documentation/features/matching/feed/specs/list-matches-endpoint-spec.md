---
title: Endpoint de listagem de matches em matching
status: em progresso
last_updated_at: 2026-02-17
---

# 1. Objetivo
Entregar o endpoint autenticado `GET /matching/{horse_id}` para listar os `matches` de um cavalo, reutilizando o `ListMatchesUseCase` ja existente e conectando o fluxo `HTTP` -> `Router` -> `Controller` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL`. A entrega deve completar a exposicao REST e garantir contrato de resposta paginada via `PaginationResponse[MatchDto]`, sem duplicar regras de negocio no controller.

# 2. Escopo

## 2.1 In-scope
- Expor endpoint `GET /matching/{horse_id}` no modulo `matching`.
- Exigir autenticacao com `Depends(AuthPipe.verify_jwt)`.
- Receber `horse_id` por path param para listar os matches do cavalo alvo.
- Reutilizar `ListMatchesUseCase.execute(horse_id)` sem criar novo `UseCase`.
- Registrar o novo controller no `MatchingRouter` e exportar em `__init__.py` do pacote de controllers `matching`.
- Ajustar ordenacao da busca no repositorio SQLAlchemy para retorno deterministico por `created_at` decrescente.

## 2.2 Out-of-scope
- Criar novo contrato de paginacao com `limit/cursor` (o endpoint segue `next_cursor=None` e `has_more=False` por ora).
- Regras de autorizacao por ownership do `horse_id` (ex.: validar se o cavalo pertence ao owner autenticado).
- Endpoint de desfazer match (`DELETE /matching/matches`) e endpoint de swipe (`POST /matching/swipes`).
- Alteracoes em schema de banco e novas migrations Alembic.
- Alteracoes em chat, notificacoes ou clientes mobile/web.

# 3. Requisitos

## 3.1 Funcionais
- O endpoint deve responder em `GET /matching/{horse_id}`.
- O endpoint deve aceitar `horse_id` como path param obrigatorio.
- O endpoint deve exigir JWT valido.
- O controller deve instanciar `ListMatchesUseCase` com `MatchesRepository` injetado por `DatabasePipe`.
- O endpoint deve retornar `HTTP 200` com `PaginationResponse[MatchDto]`.
- Quando nao houver matches, deve retornar `items=[]`, `next_cursor=null`, `has_more=false`.

## 3.2 Nao funcionais
- Controller deve permanecer magro (validar/adaptar/delegar), sem regra de negocio.
- Camada `core` deve permanecer pura, sem dependencia de `FastAPI`/`SQLAlchemy`.
- Repositorio nao deve controlar transacao (`commit/rollback` continua no middleware).
- Reutilizar componentes existentes (`ListMatchesUseCase`, `MatchDto`, `PaginationResponse`, `MatchesRepository`) para evitar duplicidade.
- Resposta deve usar contratos tipados e consistentes com o modulo `matching`.

# 4. Regras de negocio e invariantes
- **Listagem por cavalo:** somente `matches` onde o `horse_id` aparece em `horse_a_id` ou `horse_b_id`.
- **Resultado vazio e valido:** ausencia de dados nao e erro; retorna colecao vazia com `HTTP 200`.
- **Contrato de saida estavel:** retorno sempre no formato `PaginationResponse[MatchDto]`.
- **Sem regra de ownership nesta entrega:** validacao de posse do cavalo autenticado fica explicitamente fora deste escopo.
- **Autenticacao obrigatoria:** endpoint nao pode ser publico.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`ListMatchesUseCase`** (`src/equiny/core/matching/use_cases/list_matches_use_case.py`) - caso de uso pronto para listar matches por `horse_id`.
- **`MatchesRepository`** (`src/equiny/core/matching/interfaces/matches_repository.py`) - contrato com `find_many_by_horse(horse_id: Id) -> PaginationResponse[Match]`.
- **`Match` / `MatchDto`** (`src/equiny/core/matching/domain/structures/match.py`) - estrutura de dominio e DTO de saida.
- **`PaginationResponse`** (`src/equiny/core/shared/responses/pagination_response.py`) - contrato generico de resposta paginada reutilizavel.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyMatchesRepository`** (`src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py`) - implementa busca de matches por cavalo.
- **`MatchModel`** (`src/equiny/database/sqlalchemy/models/matching/match_model.py`) - mapeia a tabela `matches`.
- **`MatchesMapper`** (`src/equiny/database/sqlalchemy/mappers/matching/matches_mapper.py`) - conversao `MatchModel <-> Match`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`SwipeHorseController`** (`src/equiny/rest/controllers/matching/swipe_horse_controller.py`) - referencia de padrao no contexto `matching` para `Depends` + `UseCase`.

## 5.4 Routers (`src/equiny/routers/`)
- **`MatchingRouter`** (`src/equiny/routers/matching/matching_router.py`) - router de modulo com `prefix='/matching'`.

## 5.5 Validation (`src/equiny/validation/`)
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - alias para validar identificadores UUID na borda.

## 5.6 Pipes e Middlewares
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - injeta `MatchesRepository` via `Depends`.
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - guard de autenticacao JWT.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - controla ciclo da `Session` por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/matching/list_matches_controller.py` (**novo arquivo**)
  - **Controller:** `ListMatchesController`
  - **Rota (relativa):** `/{horse_id}`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `PaginationResponse[MatchDto]`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(DatabasePipe.get_matches_repository)`
  - **Responsabilidade:** receber `horse_id` (path), delegar para `ListMatchesUseCase` e retornar o contrato paginado.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/rest/controllers/matching/__init__.py`
  - **Mudanca:** importar e exportar `ListMatchesController` em `__all__`.
  - **Justificativa:** manter API publica do pacote de controllers `matching` consistente para composicao dos routers.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/matching/matching_router.py`
  - **Mudanca:** registrar `ListMatchesController.handle(router)` junto aos controllers existentes.
  - **Justificativa:** expor o endpoint `GET /matching/{horse_id}` no modulo `matching`.
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py`
  - **Mudanca:** ordenar `find_many_by_horse(...)` por `MatchModel.created_at.desc()` antes de mapear para dominio.
  - **Justificativa:** garantir ordem deterministica de retorno (mais recentes primeiro) para consumo por clientes.
  - **Camada:** `database`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> GET /matching/<horse_id>
  -> MatchingRouter (/matching)
  -> ListMatchesController (/matches)
       -> Depends(AuthPipe.verify_jwt)
       -> Depends(DatabasePipe.get_matches_repository)
  -> ListMatchesUseCase.execute(horse_id)
       -> MatchesRepository.find_many_by_horse(Id)
  -> SqlalchemyMatchesRepository
       -> SELECT matches WHERE horse_a_id=:id OR horse_b_id=:id ORDER BY created_at DESC
       -> MatchesMapper.to_entity(...)
  -> PaginationResponse[MatchDto]
  <- HTTP 200
```

## 9.2 Referencias internas
- `src/equiny/core/matching/use_cases/list_matches_use_case.py` (caso de uso alvo)
- `src/equiny/rest/controllers/matching/swipe_horse_controller.py` (padrao de controller no contexto)
- `src/equiny/routers/matching/matching_router.py` (composicao do modulo)
- `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py` (repositorio alvo)
- `src/equiny/rest/controllers/profiling/fetch_horse_controller.py` (referencia de endpoint `GET` com `Depends`)
