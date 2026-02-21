---
title: Endpoint para atualizar dados do owner autenticado
status: concluido
last_updated_at: 2026-02-16
---

# 1. Objetivo
Entregar o endpoint autenticado `PUT /profiling/owners` para atualizar os dados de perfil do dono logado, conectando o fluxo `HTTP` -> `Router` -> `Controller` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL`. A entrega deve reutilizar `UpdateOwnerUseCase` e `OwnersRepository`, preservar invariantes de ownership (owner sempre derivado do `JWT`) e manter o controller fino.

# 2. Escopo

## 2.1 In-scope
- Criar endpoint `PUT /profiling/owners` no contexto `profiling/owners`.
- Criar schema de validacao para payload de update do owner e conversao para `OwnerDto`.
- Reutilizar `ProfilingPipe.get_owner_id` para resolver owner autenticado (sem `owner_id` em path/query/body).
- Reutilizar `UpdateOwnerUseCase` com ajuste para garantir validacao de existencia antes do `replace`.
- Registrar controller no `OwnersRouter` e exportar no pacote de controllers.

## 2.2 Out-of-scope
- Alterar campos de onboarding fora do fluxo atual (`has_completed_onboarding` continua controlado por casos de uso de onboarding).
- Alterar identidade do owner (`id`/`account_id`) por payload HTTP.
- Criar endpoint de update parcial (`PATCH`).
- Refatoracoes amplas de nomenclatura historica fora do necessario para a feature.
- Testes automatizados (fora do escopo desta `spec`).

# 3. Requisitos

## 3.1 Funcionais
- Expor `PUT /profiling/owners` com autenticacao obrigatoria.
- Aceitar payload com os campos editaveis do owner (`name`, `email`).
- Resolver owner autenticado via `Depends(ProfilingPipe.get_owner_id)`.
- Converter payload para `OwnerDto` com `id`, `account_id` e `has_completed_onboarding` herdados do owner autenticado.
- Executar `UpdateOwnerUseCase` com `OwnersRepository` injetado por `DatabasePipe`.
- Retornar `OwnerDto` atualizado com `HTTPStatus.OK`.
- Retornar `404` quando owner nao existir no repositorio no momento do update.

## 3.2 Nao funcionais
- Controller deve permanecer magro: validar/adaptar/delegar, sem regra de negocio.
- `core` continua sem dependencia de `FastAPI`, `Depends`, `Session` ou `SQLAlchemy`.
- Repositorio SQLAlchemy nao controla transacao (`commit/rollback` continua no middleware de sessao).
- Reuso de componentes existentes (`UpdateOwnerUseCase`, `OwnersRepository`, `OwnerDto`, `ProfilingPipe`).

# 4. Regras de negocio e invariantes
- O owner alvo do update e sempre o owner da conta autenticada (`JWT.sub` -> `ProfilingPipe.get_owner_id`).
- `id` e `account_id` nao sao mutaveis por contrato HTTP.
- `has_completed_onboarding` nao deve ser alterado por este endpoint.
- Update so deve persistir se owner existir; ausencia deve resultar em erro de dominio (`OwnerNotFoundError`) e resposta `404`.
- O endpoint retorna representacao completa do owner em `OwnerDto`.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`UpdateOwnerUseCase`** (`src/equiny/core/profiling/use_cases/update_owner_use_case.py`) - caso de uso existente para substituir dados do owner via repositorio.
- **`Owner`** (`src/equiny/core/profiling/domain/entities/owner.py`) - entidade que centraliza validacoes de `Name`, `Email`, `Id` e `Logical`.
- **`OwnerDto`** (`src/equiny/core/profiling/domain/entities/dtos/owner_dto.py`) - contrato de entrada/saida usado no caso de uso.
- **`OwnerNotFoundError`** (`src/equiny/core/profiling/domain/errors/owner_not_found_error.py`) - erro de dominio para owner inexistente.
- **`OwnersRepository`** (`src/equiny/core/profiling/interfaces/repositories/owners_repository.py`) - porta com `find_by_id(...)`, `find_by_account_id(...)` e `replace(...)`.

## 5.2 Database (`src/equiny/database/`)
- **`OwnerModel`** (`src/equiny/database/sqlalchemy/models/profiling/owner_model.py`) - modelo ORM da tabela `owners`.
- **`OwnersMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/owners_mapper.py`) - mapeamento `OwnerModel <-> Owner/OwnerDto`.
- **`SqlalchemyOwnersRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_owners_repository.py`) - implementacao concreta de persistencia de owner.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`FetchOwnerController`** (`src/equiny/rest/controllers/profiling/fetch_onwer_controller.py`) - referencia de endpoint para owner autenticado usando `ProfilingPipe`.
- **`FetchOwnerHorsesController`** (`src/equiny/rest/controllers/profiling/fetch_owner_horses_controller.py`) - referencia de controller com `DatabasePipe` + `ProfilingPipe`.

## 5.4 Routers (`src/equiny/routers/`)
- **`OwnersRouter`** (`src/equiny/routers/profiling/owners_router.py`) - router com prefixo `/owners` para composicao de endpoints de owner.
- **`ProfilingRouter`** (`src/equiny/routers/profiling/profiling_router.py`) - agrega `OwnersRouter` sob prefixo `/profiling`.

## 5.5 Validation (`src/equiny/validation/`)
- **`NameSchema`** (`src/equiny/validation/shared/name_schema.py`) - alias de validacao de nome.
- **`EmailSchema`** (`src/equiny/validation/shared/email_schema.py`) - alias de validacao de email.

## 5.6 Pipes e Middlewares
- **`ProfilingPipe`** (`src/equiny/pipes/profiling_pipe.py`) - resolve owner autenticado a partir do `JWT`.
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - injeta `OwnersRepository` via sessao SQLAlchemy da request.
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - valida token Bearer e retorna payload.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - controla ciclo de transacao por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.

## 6.1 Core

## 6.1.1 Domain (Entities/Structures/Errors/Events)
- Nenhum novo arquivo.

## 6.1.2 Interfaces
- Nenhum novo arquivo.

## 6.1.3 Use Cases
- Nenhum novo arquivo.

## 6.2 Validation
- **Arquivo (novo arquivo):** `src/equiny/validation/profiling/owner_schema.py`
  - **Schema:** `OwnerSchema`
  - **Campos:** `name: NameSchema`, `email: EmailSchema`
  - **`to_dto()`**: `to_dto(owner: Owner) -> OwnerDto` (mantem `id`, `account_id` e `has_completed_onboarding` do owner autenticado e aplica campos editaveis do payload)

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
- **Arquivo (novo arquivo):** `src/equiny/rest/controllers/profiling/update_owner_controller.py`
  - **Controller:** `UpdateOwnerController`
  - **Rota (relativa):** `/`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `OwnerDto`
  - **Dependencias:** `Depends(ProfilingPipe.get_owner_id)`, `Depends(DatabasePipe.get_owner_ids_repository)`
  - **Responsabilidade:** receber `OwnerSchema`, converter para `OwnerDto`, chamar `UpdateOwnerUseCase` e retornar DTO atualizado.

## 6.6 Routers
- Nenhum novo arquivo.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/core/profiling/use_cases/update_owner_use_case.py`
  - **Mudanca:** usar `_find_owner(...)` dentro de `execute(...)` antes de `replace(...)` para garantir erro de dominio quando owner nao existir.
  - **Justificativa:** hoje o repositorio pode ignorar `replace` em owner inexistente; o caso de uso deve garantir semantica de update consistente (`404` quando nao encontrado).
  - **Camada:** `core`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** importar e exportar `UpdateOwnerController`.
  - **Justificativa:** manter API publica do pacote de controllers de profiling consistente.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/owners_router.py`
  - **Mudanca:** registrar `UpdateOwnerController.handle(router)`.
  - **Justificativa:** expor o novo endpoint sob `/profiling/owners`.
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/validation/profiling/__init__.py`
  - **Mudanca:** exportar `OwnerSchema` no pacote de validacao de profiling.
  - **Justificativa:** manter padrao de imports estaveis para schemas da camada REST.
  - **Camada:** `validation`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta entrega.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client -> PUT /profiling/owners -> ProfilingRouter -> OwnersRouter -> UpdateOwnerController
  -> Depends(ProfilingPipe.get_owner_id) -> Depends(DatabasePipe.get_owner_ids_repository)
  -> OwnerSchema.to_dto(owner)
  -> UpdateOwnerUseCase.execute(owner_dto)
  -> OwnersRepository.find_by_id(...) -> OwnersRepository.replace(...)
  -> SqlalchemyOwnersRepository -> OwnerModel (PostgreSQL)
  -> HTTP 200 (OwnerDto)
```

## 9.2 Referencias internas
- `src/equiny/rest/controllers/profiling/fetch_onwer_controller.py` (padrao de owner autenticado via `ProfilingPipe`)
- `src/equiny/rest/controllers/profiling/fetch_owner_horses_controller.py` (padrao de injecao com `DatabasePipe`)
- `src/equiny/core/profiling/use_cases/update_owner_use_case.py` (caso de uso alvo)
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_owners_repository.py` (repositorio concreto de owner)
- `src/equiny/routers/profiling/owners_router.py` (composicao do recurso `/owners`)
