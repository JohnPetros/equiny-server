---
title: Endpoint de criacao de cavalo no onboarding
status: em progresso
last_updated_at: 2026-02-15
---

## 1. Objetivo

Entregar o endpoint autenticado `POST /profiling/horses` consistente com o onboarding de `profiling` do MVP, garantindo que os dados obrigatorios do cavalo (nome, sexo, nascimento, raca e localizacao) sejam validados na borda `REST`, convertidos para `DTO` do dominio, persistidos no banco e retornados no contrato `HTTP` sem divergencias entre `Schema`, entidade, `Mapper` e `Model`.

## 2. Escopo

### 2.1 In-scope

- Ajustar o contrato de entrada (`Schema`) para incluir `sex` e `location`.
- Persistir `sex` e `location` no `HorseModel` (com `migration` Alembic).
- Corrigir criacao de `breed` no dominio para respeitar o valor enviado.
- Garantir mapeamento completo em `HorsesMapper`.

### 2.2 Out-of-scope

- Testes automatizados (regra do projeto para `spec`).
- Alteracoes de UX/app cliente.
- Endpoints adicionais alem de `POST /profiling/horses`.

## 3. Requisitos

### 3.1 Funcionais

- O endpoint exige `JWT` (via `Depends(AuthPipe.verify_jwt)`).
- Request body aceita `name`, `birth_month`, `birth_year`, `breed`, `sex` e `location`.
- A criacao persiste o cavalo e retorna `HorseDto` em `HTTP 201`.

### 3.2 Nao funcionais

- `Controller` permanece magro: valida/adapta/delega, sem regra de negocio.
- Transacao e controlada por `HandleSqlalchemySessionMiddleware` (sem `commit` no repositorio/controller).

## 4. Regras de negocio e invariantes

- `sex` aceita apenas valores suportados pelo dominio (ex: `male` e `female`).
- `location` e obrigatoria e deve conter `city` e `state`.
- `breed` deve ser mapeavel para `BreedValue` (erro de validacao caso invalida).

## 5. O que ja existe (inventario)

### 5.1 REST/Controllers (`src/equiny/rest/`)

- **`CreateHorseController`** (`src/equiny/rest/controllers/profiling/create_horse_controller.py`) - expõe `POST /profiling/horses` e delega para `CreateHorseUseCase`.
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - referencia de leitura por `horse_id`.

### 5.2 Routers (`src/equiny/routers/`)

- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - compoe as rotas de `horses`.
- **`ProfilingRouter`** (`src/equiny/routers/profiling/profiling_router.py`) - define prefixo `/profiling`.

### 5.3 Validation (`src/equiny/validation/`)

- **`HorseSchema`** (`src/equiny/validation/profiling/horse_schema.py`) - `Schema` atual de criacao; incompleto para os campos do dominio.
- **`NameSchema`** (`src/equiny/validation/shared/name_schema.py`) - validacao reutilizavel de nome.

### 5.4 Core (`src/equiny/core/`)

- **`CreateHorseUseCase`** (`src/equiny/core/profiling/use_cases/create_horse_use_case.py`) - cria entidade `Horse` e persiste via `HorsesRepository`.
- **`Horse`** (`src/equiny/core/profiling/domain/entities/horse.py`) - entidade principal; hoje cria `breed` fixo.
- **`HorseDto`** (`src/equiny/core/profiling/domain/entities/dtos/horse_dto.py`) - contrato de entrada/saida.
- **`Sex`** (`src/equiny/core/profiling/domain/structures/sex.py`) - `structure` com validacao.
- **`Location`** (`src/equiny/core/profiling/domain/structures/location.py`) - `structure` com `city/state`.
- **`Breed`** e **`BreedValue`** (`src/equiny/core/profiling/domain/structures/breed.py`) - enum/estrutura de raca.

### 5.5 Database (`src/equiny/database/`)

- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - nao armazena `sex` nem `location`.
- **`HorsesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`) - nao mapeia `sex` e `location`.
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - repositorio concreto.
- **Migration de referencia** (`alembic/versions/0a28607fd86a_remove_owner_id_atribute_from_horse_.py`) - ultima alteracao da tabela `horses`.

### 5.6 Pipes e Middlewares

- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - guard `JWT`.
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - injeta `HorsesRepository` com `Session` da request.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - ciclo transacional por request.

## 6. O que deve ser criado

### 6.1 Validation

- **Arquivo:** `src/equiny/validation/profiling/location_schema.py`
  - **Schema:** `LocationSchema`
  - **Campos:** `city: str`, `state: str`
  - **Conversao:** `to_dto() -> LocationDto`

### 6.2 Alembic (migracoes)

- **Arquivo (novo):** `alembic/versions/<revision>_add_horse_sex_and_location_columns.py`
  - **`upgrade()`**: adiciona `sex`, `location_city`, `location_state` em `horses`
  - **`downgrade()`**: remove as colunas adicionadas

## 7. O que deve ser modificado

- **Arquivo:** `src/equiny/rest/controllers/profiling/create_horse_controller.py`
  - **Mudanca:** atualizar o contrato de entrada para o `HorseSchema` completo (incluindo `sex` e `location`).
  - **Justificativa:** alinhar borda `REST` com os campos obrigatorios do PRD e do `HorseDto`.
  - **Impacto:** `rest`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/validation/profiling/horse_schema.py`
  - **Mudanca:** incluir `sex` e `location` e ajustar `to_dto()` para popular todos os campos de `HorseDto`.
  - **Justificativa:** evitar divergencia entre `Schema` e dominio.
  - **Impacto:** `validation`
  - **Compatibilidade:** quebrando (contrato do endpoint muda)

- **Arquivo:** `src/equiny/validation/profiling/__init__.py`
  - **Mudanca:** exportar `LocationSchema`.
  - **Justificativa:** padrao de exports por pacote.
  - **Impacto:** `validation`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/core/profiling/domain/structures/breed.py`
  - **Mudanca:** adicionar `Breed.create(value: str) -> Breed` com validacao contra `BreedValue`.
  - **Justificativa:** permitir `breed` dinamico, sem valor fixo.
  - **Impacto:** `core`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/core/profiling/domain/entities/horse.py`
  - **Mudanca:** trocar `Breed.create_as_arabe()` por `Breed.create(dto.breed)`.
  - **Justificativa:** respeitar o `request`.
  - **Impacto:** `core`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/database/sqlalchemy/models/profiling/horse_model.py`
  - **Mudanca:** adicionar `sex`, `location_city`, `location_state`.
  - **Justificativa:** persistir campos obrigatorios.
  - **Impacto:** `database`
  - **Compatibilidade:** quebrando (requer `migration`)

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`
  - **Mudanca:** mapear `sex` e `location` em ambos os sentidos (`Model <-> Domain`).
  - **Justificativa:** manter contrato `HorseDto` consistente.
  - **Impacto:** `database`
  - **Compatibilidade:** nao quebrando

## 8. O que deve ser removido

- **Arquivo:** `src/equiny/validation/profiling/horse_schema.py`
  - **Remocao:** versao atual de `to_dto()` que nao popula `sex` e `location`.
  - **Motivo:** elimina conversao incompleta na borda.
  - **Substituir por (se aplicavel):** `src/equiny/validation/profiling/horse_schema.py` (novo `to_dto()` completo)

## 9. Fluxo e diagramas

### 9.1 Fluxo de dados (ASCII)

```text
Client
  -> POST /profiling/horses
  -> CreateHorseController
       -> HorseSchema.validate + to_dto()
  -> CreateHorseUseCase
       -> Horse.create(HorseDto)
       -> HorsesRepository.add(Horse)
  -> SqlalchemyHorsesRepository
       -> HorsesMapper.to_model() -> HorseModel
  -> HandleSqlalchemySessionMiddleware (commit)
  <- HTTP 201 (HorseDto)
```

### 9.2 Layout (ASCII - contrato do payload)

```text
POST /profiling/horses
request body:
  name
  birth_month
  birth_year
  breed
  sex
  location
    city
    state

response 201:
  id
  name
  birth_month
  birth_year
  breed
  sex
  location
    city
    state
```

### 9.3 Referencias internas

- `src/equiny/rest/controllers/auth/sign_up_account_controller.py`
- `src/equiny/rest/controllers/profiling/fetch_horse_controller.py`
- `src/equiny/core/profiling/use_cases/create_horse_use_case.py`
- `src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`
