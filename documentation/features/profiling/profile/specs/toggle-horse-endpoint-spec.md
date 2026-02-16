---
title: Endpoint para alternar ativacao do cavalo no perfil
status: concluido
last_updated_at: 2026-02-16
---

# 1. Objetivo
Entregar o endpoint autenticado `PATCH /profiling/horses/{horse_id}/activation` para ativar/desativar o cavalo do owner logado, conectando o fluxo `REST` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL` com validacao de ownership e retorno consistente em `HorseDto`. Tecnicamente, a entrega reutiliza a capacidade de toggle da entidade `Horse` e o `ToggleHorseActivationUseCase` existente, evoluindo o contrato para evitar alteracao de cavalo de terceiros.

# 2. Escopo

## 2.1 In-scope
- Criar controller REST para `PATCH /{horse_id}/activation` no recurso `horses`.
- Registrar o controller no `HorsesRouter` sob o prefixo `/profiling/horses`.
- Evoluir `ToggleHorseActivationUseCase` para validar ownership com `owner_id` autenticado.
- Reutilizar `HorsesRepository.replace(...)` para persistir `is_active` apos toggle.
- Retornar `HorseDto` atualizado com `HTTPStatus.OK`.

## 2.2 Out-of-scope
- Criar endpoint dedicado para set explicito de status (`PATCH .../activation` com body `{ is_active: ... }`).
- Introduzir regras adicionais de elegibilidade de ativacao (ex.: bloquear ativacao sem galeria).
- Alterar contratos de `HorseSchema` ou fluxos de create/update de cavalo.
- Testes automatizados (fora do escopo desta `spec`).

# 3. Requisitos

## 3.1 Funcionais
- Expor endpoint autenticado `PATCH /profiling/horses/{horse_id}/activation`.
- Endpoint deve resolver owner autenticado via `Depends(ProfilingPipe.get_owner)`.
- Caso de uso deve buscar cavalo por `horse_id` e `owner_id` (`find_by_id_and_owner_id`).
- Se o cavalo nao existir para o owner autenticado, deve falhar com `HorseNotFoundError` (mapeado para `404`).
- Em sucesso, deve inverter `is_active`, persistir via `replace(...)` e retornar `HorseDto` atualizado.

## 3.2 Nao funcionais
- Controller deve permanecer fino, sem regra de negocio e sem acesso direto a ORM.
- `core` deve continuar puro, sem dependencias de `FastAPI`/`SQLAlchemy`.
- Persistencia nao deve controlar transacao (sem `commit/rollback` em repositorio).
- Contrato de rota deve usar `status_code` e `response_model` explicitos.

# 4. Regras de negocio e invariantes
- A acao de ativar/desativar so e permitida para cavalo pertencente ao owner autenticado.
- O estado de ativacao e binario e representado por `Horse.is_active` (`Logical` no dominio).
- Toggle sempre aplica inversao do estado atual (`True -> False`, `False -> True`).
- O endpoint nao recebe body; a transicao depende apenas do estado persistido atual do cavalo.
- Falhas de ownership/existencia devem retornar sem vazar detalhes internos da persistencia.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`Horse.toggle_activation`** (`src/equiny/core/profiling/domain/entities/horse.py`) - comportamento de dominio ja existente para inverter `is_active`.
- **`ToggleHorseActivationUseCase`** (`src/equiny/core/profiling/use_cases/toggle_horse_activation_use_case.py`) - caso de uso ja criado, hoje sem ownership e com retorno `None`.
- **`HorseNotFoundError`** (`src/equiny/core/profiling/domain/errors/horse_not_found_error.py`) - erro de dominio para ausencia de cavalo.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - interface com `find_by_id_and_owner_id(...)` e `replace(...)` necessarios ao fluxo.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - implementa busca por owner e persistencia de replace.
- **`HorsesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`) - mapeia `is_active` entre `HorseModel` e `Horse`.
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - tabela `horses` ja contem coluna `is_active`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`UpdateHorseController`** (`src/equiny/rest/controllers/profiling/update_horse_controller.py`) - referencia de endpoint autenticado com `ProfilingPipe` + `DatabasePipe` e retorno `HorseDto`.
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - referencia de rota com path param `/{horse_id}`.
- **`__init__.py` de profiling controllers** (`src/equiny/rest/controllers/profiling/__init__.py`) - ja declara `ToggleHorseActivationController`, mas o arquivo do controller ainda nao existe.

## 5.4 Routers (`src/equiny/routers/`)
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - composicao das rotas de `horses`; ainda nao registra rota de toggle.
- **`ProfilingRouter`** (`src/equiny/routers/profiling/profiling_router.py`) - aplica prefixo `/profiling`.

## 5.5 Validation (`src/equiny/validation/`)
- **`HorseDto` como `response_model`** (`src/equiny/core/profiling/domain/entities/dtos/horse_dto.py`) - contrato de resposta reaproveitavel para operacao de toggle.

## 5.6 Pipes e Middlewares
- **`ProfilingPipe`** (`src/equiny/pipes/profiling_pipe.py`) - resolve owner autenticado com base no JWT.
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - injeta `HorsesRepository` por request.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - controla ciclo transacional por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.

## 6.1 Core

## 6.1.1 Domain (Entities/Structures/Errors/Events)
- Nenhum novo arquivo.

## 6.1.2 Interfaces
- Nenhum novo arquivo.

## 6.1.3 Use Cases
- Nenhum novo arquivo (evolucao em arquivo existente).

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
- **Arquivo:** `src/equiny/rest/controllers/profiling/toggle_horse_activation_controller.py` (**novo arquivo**)
  - **Controller:** `ToggleHorseActivationController`
  - **Rota (relativa):** `/{horse_id}/activation`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `HorseDto`
  - **Dependencias:** `Depends(ProfilingPipe.get_owner)`, `Depends(DatabasePipe.get_horses_repository)`
  - **Responsabilidade:** adaptar chamada HTTP para o `ToggleHorseActivationUseCase` com `horse_id` e `owner.id.value`, retornando o DTO atualizado.

## 6.6 Routers
- Nenhum novo arquivo.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/core/profiling/use_cases/toggle_horse_activation_use_case.py`
  - **Mudanca:** alterar assinatura para `execute(horse_id: str, owner_id: str) -> HorseDto`; buscar com `find_by_id_and_owner_id(...)`; aplicar `toggle_activation()`; persistir com `replace(...)`; retornar `horse.dto`.
  - **Justificativa:** garantir seguranca por ownership e padronizar retorno de mutacao com DTO.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/routers/profiling/horses_router.py`
  - **Mudanca:** importar e registrar `ToggleHorseActivationController.handle(router)`.
  - **Justificativa:** expor o endpoint dentro do recurso correto (`/profiling/horses`).
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** manter export existente e validar consistencia de import apos criacao do novo arquivo real.
  - **Justificativa:** evitar import quebrado e garantir API publica dos controllers.
  - **Camada:** `rest`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta entrega.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> PATCH /profiling/horses/{horse_id}/activation
  -> ProfilingRouter (/profiling)
  -> HorsesRouter (/horses)
  -> ToggleHorseActivationController
       -> Depends(ProfilingPipe.get_owner)
       -> Depends(DatabasePipe.get_horses_repository)
  -> ToggleHorseActivationUseCase.execute(horse_id, owner_id)
       -> repository.find_by_id_and_owner_id(...)
       -> horse.toggle_activation()
       -> repository.replace(horse)
  -> SqlalchemyHorsesRepository.replace(...)
       -> UPDATE horses SET is_active = :value
  <- HTTP 200 (HorseDto)
```

## 9.2 Referencias internas
- `src/equiny/rest/controllers/profiling/update_horse_controller.py` (padrao de endpoint autenticado com `ProfilingPipe`)
- `src/equiny/core/profiling/use_cases/update_horse_use_case.py` (padrao de ownership por `owner_id` no use case)
- `src/equiny/rest/controllers/profiling/fetch_horse_controller.py` (padrao de uso de path param `horse_id`)
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py` (persistencia via `replace`)
