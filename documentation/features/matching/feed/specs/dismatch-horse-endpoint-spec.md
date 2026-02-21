---
title: Endpoint de dismatch de cavalos em matching
status: concluido
last_updated_at: 2026-02-17
---

# 1. Objetivo
Entregar o endpoint autenticado `DELETE /matching/matches` para remover um `match` existente entre dois cavalos, reutilizando o `DismatchHorseUseCase` ja existente e fechando o fluxo completo `HTTP` -> `Router` -> `Controller` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL`. A entrega inclui os contratos de entrada na borda REST e os ajustes minimos de consistencia na persistencia para garantir remocao correta e erro `404` quando o `match` nao existir.

# 2. Escopo

## 2.1 In-scope
- Expor endpoint `DELETE /matching/matches` no modulo `matching`.
- Exigir autenticacao via `Depends(AuthPipe.verify_jwt)`.
- Receber identificadores `horse_a_id` e `horse_b_id` por query params validados na camada `validation`.
- Reutilizar `DismatchHorseUseCase.execute(horse_a_id, horse_b_id)`.
- Corrigir a remocao no `SqlalchemyMatchesRepository.remove(...)` para excluir pelo `id` do `match` encontrado.
- Registrar o controller no `MatchingRouter` e exports de pacote necessarios.

## 2.2 Out-of-scope
- Criacao de novo caso de uso para dismatch.
- Alteracoes de schema, tabelas, indices ou migration Alembic.
- Endpoint de listagem de matches (`GET /matching/matches`).
- Regras de autorizacao avancadas (ex.: validar ownership do cavalo autenticado no `core`).
- Mudancas em feed, chat, notificacoes ou apps clientes.

# 3. Requisitos

## 3.1 Funcionais
- O endpoint deve aceitar `horse_a_id` e `horse_b_id` no request.
- O endpoint deve chamar `DismatchHorseUseCase` com os dois IDs.
- Quando o par existir (ordem A/B ou B/A), o `match` deve ser removido.
- Quando nao existir `match` para o par, deve retornar `404` via `MatchNotFoundError`.
- A resposta de sucesso deve ser `HTTP 204` sem body.
- O endpoint deve permanecer protegido por JWT.

## 3.2 Nao funcionais
- Controller deve seguir padrao magro (adaptar/delegar), sem regra de negocio.
- Camada `core` deve permanecer independente de `FastAPI` e `SQLAlchemy`.
- Repositorios nao devem executar `commit/rollback` manual.
- Contratos existentes de `MatchesRepository` devem ser preservados (sem quebra de API interna).
- Implementacao deve manter padrao de composicao por `Router` + `Controller.handle(...)`.

# 4. Regras de negocio e invariantes
- **Dismatch apenas para match existente:** nao deve remover nada silenciosamente quando nao houver par.
- **Busca por par nao ordenado:** `horse_a_id`/`horse_b_id` e `horse_b_id`/`horse_a_id` representam o mesmo `match`.
- **Remocao idempotente por contrato de erro:** repeticao da chamada apos remocao retorna `404`.
- **Autenticacao obrigatoria:** endpoint nao e publico.
- **Sem efeito colateral em swipes:** remover `match` nao remove historico de `swipes` neste escopo.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`DismatchHorseUseCase`** (`src/equiny/core/matching/use_cases/dismatch_horse_use_case.py`) - orquestra busca do `match` por par de cavalos e delega remocao ao repositorio.
- **`MatchNotFoundError`** (`src/equiny/core/matching/domain/errors/match_not_found_error.py`) - erro de dominio para `404` quando o par nao existe.
- **`MatchesRepository`** (`src/equiny/core/matching/interfaces/matches_repository.py`) - contrato com `find_by_horses(...)` e `remove(...)`.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyMatchesRepository`** (`src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py`) - implementacao concreta de persistencia de `matches`.
- **`MatchModel`** (`src/equiny/database/sqlalchemy/models/matching/match_model.py`) - modelo ORM da tabela `matches`.
- **`MatchesMapper`** (`src/equiny/database/sqlalchemy/mappers/matching/matches_mapper.py`) - conversao `MatchModel <-> Match`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`SwipeHorseController`** (`src/equiny/rest/controllers/matching/swipe_horse_controller.py`) - referencia de padrao no contexto `matching` com `Depends` e `UseCase`.

## 5.4 Routers (`src/equiny/routers/`)
- **`MatchingRouter`** (`src/equiny/routers/matching/matching_router.py`) - router de modulo com `prefix='/matching'` e registro de controllers do contexto.

## 5.5 Validation (`src/equiny/validation/`)
- **`SwipeSchema`** (`src/equiny/validation/matching/swipe_schema.py`) - referencia local de schema com `to_dto()` no contexto `matching`.
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - alias para validacao de identificadores UUID na borda.

## 5.6 Pipes e Middlewares
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - injecao de `MatchesRepository` via `Depends`.
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - guard de autenticacao JWT.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - controla ciclo transacional da sessao por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma secao nao esteja envolvida na implementacao, ignore-a na spec.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/matching/dismatch_horse_controller.py` (**novo arquivo**)
  - **Controller:** `DismatchHorseController`
  - **Rota (relativa):** `/matches`
  - **`status_code`:** `HTTPStatus.NO_CONTENT`
  - **`response_model`:** nao aplicavel
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(DatabasePipe.get_matches_repository)`
  - **Query Params:** `horse_a_id: IdSchema`, `horse_b_id: IdSchema`
  - **Observacoes:** uso de query params (mais apropriado para DELETE) em vez de body schema.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py`
  - **Mudanca:** ajustar `remove(...)` para excluir pelo par `horse_a_id`/`horse_b_id` (ordem A/B ou B/A) em vez de filtrar apenas por `horse_a_id`.
  - **Justificativa:** a implementacao anterior filtrava incorretamente por `MatchModel.id == horse_a_id`, que nao representa o match correto. Como `Match` nao tem campo `id`, a remocao deve usar o par de cavalos.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/rest/controllers/matching/__init__.py`
  - **Mudanca:** exportar `DismatchHorseController` em `__all__`.
  - **Justificativa:** manter API publica do pacote consistente para registro em router.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/matching/matching_router.py`
  - **Mudanca:** registrar `DismatchHorseController.handle(router)` junto ao controller de swipe.
  - **Justificativa:** expor o novo endpoint no modulo `matching`.
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/validation/matching/__init__.py`
  - **Mudanca:** nenhuma.
  - **Justificativa:** nao ha novo schema no pacote `validation/matching`; validacao e feita via `IdSchema` em `validation/shared` e aplicada diretamente nos query params do controller.
  - **Camada:** `validation`

- **Arquivo:** `src/equiny/core/matching/use_cases/dismatch_horse_use_case.py`
  - **Mudanca:** padronizar `raise MatchNotFoundError()` (instancia) para consistencia com demais use cases.
  - **Justificativa:** clareza semantica e padrao de erro do projeto.
  - **Camada:** `core`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> DELETE /matching/matches?horse_a_id=<id>&horse_b_id=<id>
  -> MatchingRouter (/matching)
  -> DismatchHorseController (/matches)
       -> Depends(AuthPipe.verify_jwt)
       -> Depends(DatabasePipe.get_matches_repository)
       -> Query params: horse_a_id, horse_b_id (IdSchema)
  -> DismatchHorseUseCase.execute(horse_a_id, horse_b_id)
       -> MatchesRepository.find_by_horses(a, b)
       -> MatchesRepository.remove(match)
  -> SqlalchemyMatchesRepository
  -> PostgreSQL (matches)
  <- HTTP 204 No Content
```

## 9.2 Referencias internas
- `src/equiny/core/matching/use_cases/dismatch_horse_use_case.py` (caso de uso alvo)
- `src/equiny/rest/controllers/matching/swipe_horse_controller.py` (padrao de controller no contexto)
- `src/equiny/routers/matching/matching_router.py` (composicao de endpoints do modulo)
- `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py` (repositorio alvo do ajuste)

# 10. Resumo final para PR

## 10.1 O que foi entregue

### Core (`src/equiny/core/`)
- **Use Case:** Padronizado `raise MatchNotFoundError()` com instancia (sem alterar contrato).

### Database (`src/equiny/database/`)
- **Repository:** Corrigida logica de `remove()` em `SqlalchemyMatchesRepository` para deletar pelo par de cavalos (`horse_a_id`/`horse_b_id`) considerando ambas as ordens (A/B ou B/A).

### REST (`src/equiny/rest/`)
- **Controller:** Novo `DismatchHorseController` com endpoint `DELETE /matches`.
  - Recebe `horse_a_id` e `horse_b_id` como query params (UUID validados via `IdSchema`).
  - Protegido por `AuthPipe.verify_jwt`.
  - Retorna `HTTP 204 No Content` em sucesso.
  - Propaga `MatchNotFoundError` como `HTTP 404`.
- **Exports:** `DismatchHorseController` adicionado ao `__all__` do pacote.

### Routers (`src/equiny/routers/`)
- **Router:** `DismatchHorseController.handle()` registrado em `MatchingRouter`.

## 10.2 Validacoes executadas

```bash
# Lint/format
$ poe codecheck
All checks passed!

# Type check
$ poe typecheck
0 errors, 0 warnings, 0 informations

# Tests
$ poe test
48 passed
```

## 10.3 Checklist de arquitetura

- [x] `core` puro: sem FastAPI, SQLAlchemy, HTTP, env vars
- [x] `database`: apenas persistencia/mapeamento, sem regra de negocio
- [x] `rest`: controller magro (valida/adapta/delega)
- [x] Repositorio sem `commit/rollback` manual (transacao por middleware)
- [x] Contratos de `MatchesRepository` preservados
- [x] Padrao de composicao `Router` + `Controller.handle(...)` mantido

## 10.4 Decisoes de implementacao

| Aspecto | Decisao | Justificativa |
|---------|---------|---------------|
| Query params vs Body | Query params | Mais apropriado para operacao DELETE (idempotente, sem body) |
| Remocao no repository | Por par de cavalos | Match nao tem campo `id`; remocao usa `horse_a_id`/`horse_b_id` em ambas as ordens |
| Schema de validacao | `IdSchema` reutilizado | Evita duplicacao; validacao de UUID ja existente em `validation/shared` |

## 10.5 Riscos e limitacoes

- **Autorizacao:** Endpoint verifica JWT mas nao valida se o cavalo autenticado pertence ao usuario. Escopo conforme out-of-scope da spec.
- **Idempotencia:** Chamadas repetidas retornam `404` apos remocao (comportamento esperado).
- **Sem efeito em swipes:** Historico de likes/dislikes permanece inalterado (escopo conforme spec).

## 10.6 Endpoint exposto

```
DELETE /matching/matches?horse_a_id=<uuid>&horse_b_id=<uuid>

Headers:
  Authorization: Bearer <jwt_token>

Query Params:
  horse_a_id: UUID (obrigatorio)
  horse_b_id: UUID (obrigatorio)

Responses:
  204 No Content - Match removido com sucesso
  404 Not Found - Match nao encontrado para o par de cavalos
  401 Unauthorized - Token JWT invalido ou ausente
  422 Unprocessable Entity - Parametros invalidos (nao UUID)
```
