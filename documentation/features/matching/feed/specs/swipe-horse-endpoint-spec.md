---
title: Endpoint de swipe de cavalos em matching
status: concluido
last_updated_at: 2026-02-17
---

# 1. Objetivo
Entregar o endpoint autenticado `POST /matching/swipes` para registrar `like`/`dislike` entre cavalos e criar `match` automaticamente quando houver curtida mutua, conectando o fluxo completo `HTTP` -> `Router` -> `Controller` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL`. A implementacao deve reutilizar o que ja existe em `core/matching` e complementar adaptadores de `rest`, `database`, `pipes` e `routers`, com correcoes minimas de consistencia de regra (decisao unica por par e deteccao correta de reciprocidade).

# 2. Escopo

## 2.1 In-scope
- Expor o endpoint `POST /matching/swipes` com autenticacao via `JWT`.
- Criar camada REST para swipe (controller + router).
- Criar schema de entrada em `validation` com `to_dto()` para `SwipeDto`.
- Implementar repositorios SQLAlchemy de `swipes` e `matches` aderentes aos contratos do `core`.
- Criar models/mappers SQLAlchemy para persistencia de `swipes` e `matches`.
- Criar migration Alembic para tabelas/indices necessarios.
- Ajustar `DatabasePipe` e `app.py` para composicao e DI.
- Ajustar `SwipeHorseUseCase` para validar duplicidade de swipe e reciprocidade correta.

## 2.2 Out-of-scope
- Endpoint para listar `matches` (`GET /matching/matches`).
- Endpoint para desfazer `match` (`DELETE /matching/matches/...`).
- Feed de recomendacao e filtros de descoberta.
- Notificacoes/eventos assincronos de novo `match`.
- Alteracoes em UI/mobile.

# 3. Requisitos

## 3.1 Funcionais
- O endpoint deve aceitar payload com `from_horse_id`, `to_horse_id` e `decision` (`like` | `dislike`).
- O endpoint deve exigir autenticacao (`Depends(AuthPipe.verify_jwt)` de forma direta ou indireta).
- O endpoint deve executar `SwipeHorseUseCase.execute(dto)` e retornar o `SwipeDto` retornado pelo caso de uso.
- O sistema deve registrar somente uma decisao por par ordenado (`from_horse_id`, `to_horse_id`).
- Ao receber `like` reciproco (`A -> B` e `B -> A`), deve criar um unico `match` entre os dois cavalos.
- O endpoint deve retornar `HTTP 201` com `SwipeDto`, sem expor models ORM.

## 3.2 Nao funcionais
- Controller deve permanecer magro (adaptar/validar/delegar).
- `core` deve continuar puro, sem dependencia de `FastAPI`/`SQLAlchemy`.
- Repositorios nao devem executar `commit/rollback`.
- Persistencia deve ser versionada com migration Alembic.
- Contratos de interfaces do `core` devem ser respeitados exatamente nas implementacoes.

# 4. Regras de negocio e invariantes
- **Decisao unica por par ordenado:** nao pode existir mais de um swipe para o mesmo `from_horse_id` e `to_horse_id`.
- **Match apenas com reciprocidade de like:** `dislike` nunca gera `match`.
- **Match unico por par nao ordenado:** uma vez criado entre `horse_a` e `horse_b`, nao deve duplicar.
- **Ordem do fluxo:** primeiro valida/regras, depois persistencia da decisao, com criacao de `match` quando aplicavel.
- **Autenticacao obrigatoria:** endpoint de swipe nao pode ser publico.
- **Contrato de saida do endpoint:** a resposta deve refletir exatamente o `SwipeDto` produzido pelo `UseCase`.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`SwipeHorseUseCase`** (`src/equiny/core/matching/use_cases/swipe_horse_use_case.py`) - orquestra criacao do `Swipe` e eventual criacao de `Match`.
- **`Swipe`** (`src/equiny/core/matching/domain/structures/swipe.py`) - estrutura de dominio com `verify_match(...)`.
- **`SwipeDto`** (`src/equiny/core/matching/domain/structures/dtos/swipe_dto.py`) - contrato de entrada do caso de uso.
- **`Match` / `MatchDto`** (`src/equiny/core/matching/domain/structures/match.py`) - estrutura de conexao gerada por curtida mutua.
- **`SwipesRepository`** (`src/equiny/core/matching/interfaces/swipes_repository.py`) - porta de persistencia de swipes.
- **`MatchesRepository`** (`src/equiny/core/matching/interfaces/matches_repository.py`) - porta de persistencia de matches.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyRepository`** (`src/equiny/database/sqlalchemy/repositories/sqlalchemy_repository.py`) - base para repositorios concretos com `Session`.
- **`Model`** (`src/equiny/database/sqlalchemy/models/model.py`) - base declarativa com `created_at` e `updated_at`.
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - referencia de tabela de cavalos para chaves estrangeiras.
- **`alembic/env.py`** (`alembic/env.py`) - composition root de metadata das migrations.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`CreateHorseController`** (`src/equiny/rest/controllers/profiling/create_horse_controller.py`) - referencia de padrao `Controller.handle(router)` + `Depends(...)`.
- **`SignInAccountController`** (`src/equiny/rest/controllers/auth/sign_in_account_controller.py`) - referencia de endpoint autenticado e schema local.

## 5.4 Routers (`src/equiny/routers/`)
- **`ProfilingRouter`** (`src/equiny/routers/profiling/profiling_router.py`) - referencia de router de modulo com `prefix` e `tags`.
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - referencia de registro de controllers por recurso.

## 5.5 Validation (`src/equiny/validation/`)
- **`Schema`** (`src/equiny/validation/shared/schema.py`) - alias base para schemas Pydantic no projeto.
- **`HorseSchema`** (`src/equiny/validation/profiling/horse_schema.py`) - referencia de `to_dto()`.

## 5.6 Pipes e Middlewares
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - provedor de repositorios SQLAlchemy por `Depends`.
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - validacao de `Bearer JWT`.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - ciclo transacional por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma secao nao esteja envolvida na implementacao, ignore-a na spec.

## 6.1 Core

## 6.1.1 Domain (Entities/Structures/Errors/Events)
- **Arquivo:** `src/equiny/core/matching/domain/errors/swipe_already_registered_error.py` (**novo arquivo**)
  - **Tipo:** `error`
  - **Responsabilidade:** representar violacao da regra de decisao unica por par ordenado.
  - **Assinatura/contratos:** `class SwipeAlreadyRegisteredError(ConflictError)`.
  - **Dependencias:** `equiny.core.shared.domain.errors.ConflictError`.
  - **Observacoes:** mensagem deve identificar `from_horse_id` e `to_horse_id` para depuracao.

## 6.1.2 Interfaces
- Nenhum novo arquivo.

## 6.1.3 Use Cases
- Nenhum novo arquivo.

## 6.2 Validation
- **Arquivo:** `src/equiny/validation/matching/swipe_schema.py` (**novo arquivo**)
  - **Schema:** `SwipeSchema`
  - **Campos:** `from_horse_id: str`, `to_horse_id: str`, `decision: SwipeDecisionValue`
  - **`to_dto()`**: `-> SwipeDto` (com `created_at=datetime.now()`)

- **Arquivo:** `src/equiny/validation/matching/__init__.py` (**novo arquivo**)
  - **Schema:** export do pacote
  - **Campos:** nao aplicavel
  - **`to_dto()`**: nao aplicavel

## 6.3 Database

## 6.3.1 Models
- **Arquivo:** `src/equiny/database/sqlalchemy/models/matching/swipe_model.py` (**novo arquivo**)
  - **Model:** `SwipeModel`
  - **Tabela:** `swipes`
  - **Campos/indices:** `id` (PK), `from_horse_id` (FK `horses.id`, index), `to_horse_id` (FK `horses.id`, index), `decision`, `created_at`, `updated_at`, `unique(from_horse_id, to_horse_id)`.

- **Arquivo:** `src/equiny/database/sqlalchemy/models/matching/match_model.py` (**novo arquivo**)
  - **Model:** `MatchModel`
  - **Tabela:** `matches`
  - **Campos/indices:** `id` (PK), `horse_a_id` (FK `horses.id`, index), `horse_b_id` (FK `horses.id`, index), `created_at`, `updated_at`, indice unico para par normalizado (`least(horse_a_id, horse_b_id)`, `greatest(horse_a_id, horse_b_id)`) ou estrategia equivalente.

- **Arquivo:** `src/equiny/database/sqlalchemy/models/matching/__init__.py` (**novo arquivo**)
  - **Model:** export do pacote
  - **Tabela:** nao aplicavel
  - **Campos/indices:** nao aplicavel

## 6.3.2 Mappers
- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/matching/swipes_mapper.py` (**novo arquivo**)
  - **Mapper:** `SwipesMapper`
  - **Conversao:** `SwipeModel <-> Swipe`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/matching/matches_mapper.py` (**novo arquivo**)
  - **Mapper:** `MatchesMapper`
  - **Conversao:** `MatchModel <-> Match`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/matching/__init__.py` (**novo arquivo**)
  - **Mapper:** export do pacote
  - **Conversao:** nao aplicavel

## 6.3.3 Repositories
- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_swipes_repository.py` (**novo arquivo**)
  - **Repository:** `SqlalchemySwipesRepository`
  - **Implementa:** `SwipesRepository`
  - **Metodos:** `add(...)`, `find_by_horses(...)`, `find_by_to_horse_id(...)` (se mantido no contrato)

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py` (**novo arquivo**)
  - **Repository:** `SqlalchemyMatchesRepository`
  - **Implementa:** `MatchesRepository`
  - **Metodos:** `add(...)`, `find_by_horses(...)`, `find_many_by_horse(...)`, `remove(...)`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/matching/__init__.py` (**novo arquivo**)
  - **Repository:** export do pacote
  - **Implementa:** nao aplicavel
  - **Metodos:** nao aplicavel

## 6.3.4 Migracoes (Alembic)
- **Mudanca de schema:** criacao das tabelas `swipes` e `matches`, com FKs para `horses`, indices de busca e unicidade para evitar duplicidade de decisao e de match.
- **Nova migration:** `alembic/versions/<revision>_add_matching_swipes_and_matches_tables.py` (**novo arquivo**)

## 6.4 Pipes
- Nenhum novo arquivo.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/matching/swipe_horse_controller.py` (**novo arquivo**)
  - **Controller:** `SwipeHorseController`
  - **Rota (relativa):** `/swipes`
  - **`status_code`:** `HTTPStatus.CREATED`
  - **`response_model`:** `SwipeDto`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(DatabasePipe.get_swipes_repository)`, `Depends(DatabasePipe.get_matches_repository)`

- **Arquivo:** `src/equiny/rest/controllers/matching/__init__.py` (**novo arquivo**)
  - **Controller:** export do pacote
  - **Rota (relativa):** nao aplicavel
  - **`status_code`:** nao aplicavel
  - **`response_model`:** nao aplicavel
  - **Dependencias:** nao aplicavel

## 6.6 Routers
- **Arquivo:** `src/equiny/routers/matching/matching_router.py` (**novo arquivo**)
  - **Router:** `MatchingRouter`
  - **Prefixo:** `/matching`
  - **Controllers:** `SwipeHorseController.handle(...)`

- **Arquivo:** `src/equiny/routers/matching/__init__.py` (**novo arquivo**)
  - **Router:** export do pacote
  - **Prefixo:** nao aplicavel
  - **Controllers:** nao aplicavel

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/core/matching/use_cases/swipe_horse_use_case.py`
  - **Mudanca:** corrigir consulta de reciprocidade para buscar swipe reverso correto, validar duplicidade antes de adicionar novo swipe e ajustar retorno para `SwipeDto`.
  - **Justificativa:** evitar falso positivo/falso negativo de `match`, cumprir regra de decisao unica por par e alinhar contrato REST para retornar o resultado do `UseCase`.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/matching/interfaces/swipes_repository.py`
  - **Mudanca:** ajustar assinatura para retorno opcional e incluir busca por par (`find_by_horses`) para suportar regra de unicidade e reciprocidade.
  - **Justificativa:** contrato atual nao cobre os cenarios necessarios sem ambiguidade.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/matching/domain/errors/__init__.py`
  - **Mudanca:** exportar `SwipeAlreadyRegisteredError`.
  - **Justificativa:** manter API publica de erros do contexto `matching`.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/pipes/database_pipe.py`
  - **Mudanca:** adicionar providers `get_swipes_repository(...)` e `get_matches_repository(...)`.
  - **Justificativa:** seguir padrao DI via `Depends(DatabasePipe.*)` em controllers.
  - **Camada:** `pipes/middlewares`

- **Arquivo:** `src/equiny/app.py`
  - **Mudanca:** incluir `MatchingRouter.register()` na composicao da aplicacao.
  - **Justificativa:** expor o endpoint na API.
  - **Camada:** `routers`

- **Arquivo:** `alembic/env.py`
  - **Mudanca:** importar `SwipeModel` e `MatchModel` para registrar metadata.
  - **Justificativa:** permitir autogenerate e aplicacao correta das migrations.
  - **Camada:** `database`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> POST /matching/swipes
  -> MatchingRouter (/matching)
  -> SwipeHorseController (/swipes)
       -> Depends(AuthPipe.verify_jwt)
       -> Depends(DatabasePipe.get_swipes_repository)
       -> Depends(DatabasePipe.get_matches_repository)
       -> body SwipeSchema.to_dto()
  -> SwipeHorseUseCase.execute(dto)
       -> SwipesRepository.find_by_horses(from, to) [duplicidade]
       -> SwipesRepository.find_by_horses(to, from) [reciprocidade]
       -> MatchesRepository.add(match) [quando like mutuo]
       -> SwipesRepository.add(swipe)
  -> Sqlalchemy*Repository (mappers)
  -> PostgreSQL (tabelas swipes/matches)
  <- HTTP 201 + SwipeDto
```

## 9.2 Referencias internas
- `src/equiny/core/matching/use_cases/swipe_horse_use_case.py` (caso de uso alvo)
- `src/equiny/rest/controllers/profiling/create_horse_controller.py` (padrao de controller)
- `src/equiny/routers/profiling/profiling_router.py` (padrao de router de modulo)
- `src/equiny/pipes/database_pipe.py` (padrao de DI de repositorio)
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py` (padrao de repositorio SQLAlchemy)

# 10. Implementacao realizada

## 10.1 Arquivos criados (17 novos)
- `src/equiny/core/matching/domain/errors/swipe_already_registered_error.py`
- `src/equiny/validation/matching/swipe_schema.py`
- `src/equiny/validation/matching/__init__.py`
- `src/equiny/database/sqlalchemy/models/matching/swipe_model.py`
- `src/equiny/database/sqlalchemy/models/matching/match_model.py`
- `src/equiny/database/sqlalchemy/models/matching/__init__.py`
- `src/equiny/database/sqlalchemy/mappers/matching/swipes_mapper.py`
- `src/equiny/database/sqlalchemy/mappers/matching/matches_mapper.py`
- `src/equiny/database/sqlalchemy/mappers/matching/__init__.py`
- `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_swipes_repository.py`
- `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py`
- `src/equiny/database/sqlalchemy/repositories/matching/__init__.py`
- `src/equiny/rest/controllers/matching/swipe_horse_controller.py`
- `src/equiny/rest/controllers/matching/__init__.py`
- `src/equiny/routers/matching/matching_router.py`
- `src/equiny/routers/matching/__init__.py`
- `alembic/versions/1980133d6f77_add_matching_swipes_and_matches_tables.py`

## 10.2 Arquivos modificados (7)
- `src/equiny/core/matching/domain/structures/swipe.py` - Adicionada propriedade `dto`
- `src/equiny/core/matching/interfaces/swipes_repository.py` - Adicionado `find_by_horses()`, retorno opcional
- `src/equiny/core/matching/use_cases/swipe_horse_use_case.py` - Validacao de duplicidade, reciprocidade correta, retorno `SwipeDto`
- `src/equiny/core/matching/domain/errors/__init__.py` - Export do `SwipeAlreadyRegisteredError`
- `src/equiny/pipes/database_pipe.py` - Providers `get_swipes_repository()` e `get_matches_repository()`
- `src/equiny/app.py` - Registro do `MatchingRouter`
- `alembic/env.py` - Import dos models `SwipeModel` e `MatchModel`

## 10.3 Decisoes tomadas
- **ID gerado automaticamente:** Models utilizam `uuid4().hex` como default para PK
- **Indice unico de match:** Implementado com `Index('ix_matches_pair', 'horse_a_id', 'horse_b_id', unique=True)`
- **Constraint de swipe:** Implementado com `UniqueConstraint('from_horse_id', 'to_horse_id', name='uq_swipe_pair')`

## 10.4 Validacao
- `poe codecheck`: All checks passed, 234 files formatted
- `poe typecheck`: 0 errors, 0 warnings, 0 informations
- `poe test`: 41 passed
- Migration aplicada com sucesso
/create-pr specs: documentation/features/matching/feed/specs/swipe-horse-endpoint-spec.md
documentation/features/matching/feed/specs/dismatch-horse-endpoint-spec.md issue