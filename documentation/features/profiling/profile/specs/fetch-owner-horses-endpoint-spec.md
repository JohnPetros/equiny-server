---
title: Endpoint para listar cavalos do owner autenticado
status: concluida
last_updated_at: 2026-02-16
---

# 1. Objetivo
Entregar o endpoint autenticado `GET /profiling/owners/me/horses` para retornar os cavalos do owner autenticado, conectando o fluxo completo `REST` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL` com resposta tipada em `list[HorseDto]`. A entrega deve reutilizar o `GetOwnerHorsesUseCase` ja existente, obtendo `owner_id` via `ProfilingPipe.get_owner_id` e completando os pontos faltantes de exposicao HTTP e persistencia.

# 2. Escopo

## 2.1 In-scope
- Criar controller REST para listar cavalos do owner autenticado (`/me/horses`).
- Registrar a rota no `OwnersRouter` sob o prefixo de `profiling`.
- Reutilizar `GetOwnerHorsesUseCase` no `core`, mantendo controller magro.
- Implementar no `SqlalchemyHorsesRepository` o metodo `find_many_by_owner(...)` exigido pela interface `HorsesRepository`.
- Expor resposta com `HTTPStatus.OK` e `response_model=list[HorseDto]`.

## 2.2 Out-of-scope
- Criar endpoint alternativo para buscar cavalos de owner arbitrario por path param (`/{owner_id}/horses`).
- Introduzir paginacao, filtros ou ordenacao customizada para a listagem.
- Alterar contrato de dominio para validar existencia do owner antes de listar (nesta entrega, owner autenticado sem cavalos retorna lista vazia).
- Refactor de nomenclaturas historicas fora do necessario para a feature (ex.: `horsers_repository.py`, `fetch_onwer_controller.py`).
- Testes automatizados (fora do escopo desta `spec`).

# 3. Requisitos

## 3.1 Funcionais
- Expor `GET /profiling/owners/me/horses`.
- Endpoint deve exigir autenticacao e resolver owner via `Depends(ProfilingPipe.get_owner_id)`.
- Endpoint deve repassar `owner.id.value` para `GetOwnerHorsesUseCase.execute(owner_id)`.
- O `UseCase` deve retornar `list[HorseDto]` a partir de `HorsesRepository.find_many_by_owner(Id.create(owner_id))`.
- Em sucesso, retornar `HTTP 200` com array de `HorseDto`.
- Quando nao houver cavalos para o owner autenticado, retornar `HTTP 200` com lista vazia.

## 3.2 Nao funcionais
- Controller deve permanecer fino, sem regra de negocio e sem acesso direto a ORM.
- Implementacao deve manter o `core` puro (sem dependencias de `FastAPI`/`SQLAlchemy`).
- Repositorio SQLAlchemy nao deve fazer `commit/rollback` (transacao continua no middleware por request).
- O endpoint deve seguir padrao arquitetural do projeto: dependencias via `Depends(...)` e `Pipe`.

# 4. Regras de negocio e invariantes
- O identificador do owner deve ser derivado exclusivamente do `ProfilingPipe.get_owner_id`.
- O endpoint exige autenticacao e resolucao de owner antes de executar o caso de uso.
- A listagem de cavalos e derivada exclusivamente do vinculo `Horse.owner_id` na persistencia.
- O retorno e sempre uma colecao (`list[HorseDto]`), inclusive quando vazia.
- Nao deve haver entrada de `owner_id` por path/query/body para evitar escalonamento horizontal indevido.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`GetOwnerHorsesUseCase`** (`src/equiny/core/profiling/use_cases/get_owner_id_horses_use_case.py`) - caso de uso ja criado para listar cavalos por owner, pronto para reutilizacao.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - contrato ja define `find_many_by_owner(owner_id: Id) -> list[Horse]`.
- **`HorseDto`** (`src/equiny/core/profiling/domain/entities/dtos/horse_dto.py`) - DTO de saida da listagem.

## 5.2 Database (`src/equiny/database/`)
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - modelo ORM com coluna `owner_id` usada como criterio de busca.
- **`HorsesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`) - conversao `HorseModel -> Horse` para retorno ao `UseCase`.
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - repositorio concreto que ainda nao implementa `find_many_by_owner(...)`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - referencia de endpoint `GET` com `response_model=HorseDto` e uso de `DatabasePipe`.
- **`FetchOwnerController`** (`src/equiny/rest/controllers/profiling/fetch_onwer_controller.py`) - referencia de endpoint que resolve owner autenticado via `ProfilingPipe.get_owner_id`.

## 5.4 Routers (`src/equiny/routers/`)
- **`OwnersRouter`** (`src/equiny/routers/profiling/owners_router.py`) - ponto de composicao das rotas de proprietario (`/owners`).
- **`ProfilingRouter`** (`src/equiny/routers/profiling/profiling_router.py`) - agrega sub-routers e aplica prefixo `/profiling`.

## 5.5 Validation (`src/equiny/validation/`)
- **`HorseDto` como `response_model` direto** (`src/equiny/core/profiling/domain/entities/dtos/horse_dto.py`) - padrao atual do projeto para respostas simples sem schema intermediario de listagem.

## 5.6 Pipes e Middlewares
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - fornece `HorsesRepository` com `Session` da request.
- **`ProfilingPipe`** (`src/equiny/pipes/profiling_pipe.py`) - resolve owner autenticado a partir do `JWT` e `OwnersRepository`.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - controla ciclo de vida transacional por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.

## 6.1 Core

## 6.1.1 Domain (Entities/Structures/Errors/Events)
- Nenhum novo arquivo.

## 6.1.2 Interfaces
- Nenhum novo arquivo.

## 6.1.3 Use Cases
- Nenhum novo arquivo (reuso de `GetOwnerHorsesUseCase`).

## 6.2 Validation
- Nenhum novo arquivo.

## 6.3 Database

## 6.3.1 Models
- Nenhum novo arquivo.

## 6.3.2 Mappers
- Nenhum novo arquivo.

## 6.3.3 Repositories
- Nenhum novo arquivo.

## 6.3.4 Migracoes (Alembic)
- **Mudanca de schema:** nenhuma.
- **Nova migration:** nao aplicavel.

## 6.4 Pipes
- Nenhum novo arquivo.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/profiling/fetch_owner_horses_controller.py` (**novo arquivo**)
  - **Controller:** `FetchOwnerHorsesController`
  - **Rota (relativa):** `/me/horses`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `list[HorseDto]`
  - **Dependencias:** `Depends(ProfilingPipe.get_owner_id)`, `Depends(DatabasePipe.get_horses_repository)`
  - **Responsabilidade:** obter owner autenticado no Pipe, delegar para o caso de uso com `owner.id.value` e retornar lista tipada.

## 6.6 Routers
- Nenhum novo arquivo.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
  - **Mudanca:** implementar `find_many_by_owner(owner_id: Id) -> list[Horse]` com query por `HorseModel.owner_id` e mapeamento por `HorsesMapper.to_entity`.
  - **Justificativa:** cumprir contrato de `HorsesRepository` usado por `GetOwnerHorsesUseCase`.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** importar e exportar `FetchOwnerHorsesController` no `__all__`.
  - **Justificativa:** manter API publica de controllers de profiling consistente com o padrao do projeto.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/owners_router.py`
  - **Mudanca:** registrar `FetchOwnerHorsesController.handle(router)` junto ao `FetchOwnerController`.
  - **Justificativa:** expor endpoint no recurso correto (`/profiling/owners`).
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/core/profiling/use_cases/get_owner_id_horses_use_case.py`
  - **Mudanca:** manter assinatura atual e padronizar nomenclatura interna (`horsers` -> `horses`) para clareza sem alterar contrato.
  - **Justificativa:** melhoria de legibilidade mantendo compatibilidade funcional.
  - **Camada:** `core`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta entrega.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> GET /profiling/owners/me/horses
  -> ProfilingRouter (/profiling)
  -> OwnersRouter (/owners)
  -> FetchOwnerHorsesController
       -> Depends(ProfilingPipe.get_owner_id)
       -> Depends(DatabasePipe.get_horses_repository)
  -> GetOwnerHorsesUseCase.execute(owner.id.value)
  -> HorsesRepository.find_many_by_owner(Id)
  -> SqlalchemyHorsesRepository.find_many_by_owner(...)
       -> SELECT horses WHERE owner_id = :authenticated_owner_id
       -> HorsesMapper.to_entity(...)
  -> list[HorseDto]
  <- HTTP 200
```

## 9.2 Referencias internas
- `src/equiny/rest/controllers/profiling/fetch_horse_controller.py` (padrao de `GET` com `DatabasePipe`)
- `src/equiny/rest/controllers/profiling/fetch_onwer_controller.py` (padrao de resolucao de owner autenticado via `ProfilingPipe`)
- `src/equiny/routers/profiling/owners_router.py` (ponto de registro do novo controller)
- `src/equiny/core/profiling/use_cases/get_owner_id_horses_use_case.py` (caso de uso reutilizado)
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py` (repositorio alvo para implementar a busca)
