---
title: Endpoint para atualizar dados do cavalo no perfil
status: concluido
last_updated_at: 2026-02-16
---

# 1. Objetivo
Entregar o endpoint autenticado `PUT /profiling/horses/{horse_id}` para atualizar os dados do cavalo do dono logado na tela de perfil, conectando corretamente `REST` -> `UseCase` -> `Repository` -> `SQLAlchemy`, com controle de ownership, persistencia de `is_active` e retorno consistente em `HorseDto`.

# 2. Escopo

## 2.1 In-scope
- Criar controller de atualizacao de cavalo em `REST` e registrar no router de `horses`.
- Reutilizar `UpdateHorseUseCase` com ajustes de assinatura para garantir ownership e uso do `horse_id` vindo do path.
- Implementar metodos faltantes de substituicao no repositorio SQLAlchemy (`replace` e `replace_gallery`) para aderir ao contrato `HorsesRepository`.
- Persistir e mapear `is_active` no banco (`Model`, `Mapper` e `Migration` Alembic).
- Ajustar `HorseSchema` para gerar `HorseDto` completo (incluindo `is_active`) usado no fluxo de update.

## 2.2 Out-of-scope
- Criacao de endpoint de update parcial (`PATCH`) com merge por campo.
- Regras avancadas de elegibilidade para ativacao (ex.: bloquear `is_active=True` sem foto) nesta entrega.
- Alteracoes de UX/frontend da tela de perfil.
- Testes automatizados (fora do escopo desta `spec`).

# 3. Requisitos

## 3.1 Funcionais
- Expor `PUT /profiling/horses/{horse_id}` em `/profiling/horses`.
- Endpoint deve exigir autenticacao e resolver dono via `Depends(ProfilingPipe.get_owner)`.
- Endpoint deve aceitar payload de cavalo e converter para `HorseDto` com `to_dto()`.
- Atualizacao deve ocorrer apenas para cavalo que pertence ao dono autenticado.
- Retornar `HorseDto` atualizado com `HTTP 200`.
- Retornar `404` quando cavalo nao existir ou nao pertencer ao dono.

## 3.2 Nao funcionais
- Controller deve permanecer magro (sem regra de negocio; apenas adaptar/delegar).
- `core` permanece sem dependencias de `FastAPI`/`SQLAlchemy`.
- Repositorio nao deve executar `commit/rollback` (transacao continua no middleware de sessao).
- Contrato da interface `HorsesRepository` deve ser implementado integralmente na camada SQLAlchemy.

# 4. Regras de negocio e invariantes
- `horse_id` do path e a fonte de verdade da identidade do agregado atualizado.
- Update de perfil de cavalo e operacao autenticada e escopada ao dono logado.
- `Horse` continua sendo reconstruido por `Horse.create(HorseDto)`; por isso o `HorseDto` de update deve ser completo.
- `is_active` e propriedade booleana persistida do cavalo e deve trafegar em `Schema`, `DTO`, `Mapper` e `Model`.
- Violacoes de existencia/ownership devem subir erro de dominio (`HorseNotFoundError`) para o handler global traduzir para `HTTP 404`.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`UpdateHorseUseCase`** (`src/equiny/core/profiling/use_cases/update_horse_use_case.py`) - caso de uso existente para update, hoje sem validacao de ownership e sem garantir `id` vindo do path.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - contrato ja define `replace(...)` e `find_by_id_and_owner_id(...)`.
- **`HorseDto`** (`src/equiny/core/profiling/domain/entities/dtos/horse_dto.py`) - DTO de entrada/saida contendo `is_active` como campo obrigatorio.
- **`HorseNotFoundError`** (`src/equiny/core/profiling/domain/errors/horse_not_found_error.py`) - erro de dominio para ausencia de cavalo.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - repositorio concreto sem implementacao atual de `replace(...)`/`replace_gallery(...)`.
- **`HorsesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`) - mapeia `Horse <-> HorseModel`, mas nao mapeia `is_active`.
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - tabela `horses` sem coluna `is_active`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`CreateHorseController`** (`src/equiny/rest/controllers/profiling/create_horse_controller.py`) - referencia de controller com `HorseSchema` e `DatabasePipe`.
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - referencia de endpoint com `/{horse_id}`.

## 5.4 Routers (`src/equiny/routers/`)
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - ponto de composicao das rotas de `horses`.
- **`ProfilingRouter`** (`src/equiny/routers/profiling/profiling_router.py`) - prefixo modulo `/profiling`.

## 5.5 Validation (`src/equiny/validation/`)
- **`HorseSchema`** (`src/equiny/validation/profiling/horse_schema.py`) - schema reutilizavel para dados do cavalo; atualmente nao popula `is_active` no `HorseDto`.
- **`LocationSchema`** (`src/equiny/validation/profiling/location_schema.py`) - schema aninhado de localizacao usado no payload do cavalo.

## 5.6 Pipes e Middlewares
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - injeta `HorsesRepository` via sessao da request.
- **`ProfilingPipe`** (`src/equiny/pipes/profiling_pipe.py`) - resolve `Owner` da conta autenticada.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - controla ciclo transacional por request.

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
- Nenhum novo arquivo (reuso de `HorseSchema`).

## 6.3 Database

## 6.3.1 Models
- Nenhum novo arquivo.

## 6.3.2 Mappers
- Nenhum novo arquivo.

## 6.3.3 Repositories
- Nenhum novo arquivo.

## 6.3.4 Migracoes (Alembic)
- **Mudanca de schema:** adicionar coluna booleana `is_active` em `horses` com `server_default=false` para backfill e remover default ao final da migration.
- **Nova migration (novo arquivo):** `alembic/versions/<revision>_add_is_active_to_horses.py`.

## 6.4 Pipes
- Nenhum novo arquivo.

## 6.5 REST 

### 6.5.1 Controllers
- **Arquivo (novo arquivo):** `src/equiny/rest/controllers/profiling/update_horse_controller.py`
  - **Controller:** `UpdateHorseController`
  - **Rota (relativa):** `/{horse_id}`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `HorseDto`
  - **Dependencias:** `Depends(ProfilingPipe.get_owner)`, `Depends(DatabasePipe.get_horses_repository)`
  - **Responsabilidade:** adaptar payload para `HorseDto`, delegar para `UpdateHorseUseCase` e retornar resultado.

## 6.6 Routers
- Nenhum novo arquivo.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/core/profiling/use_cases/update_horse_use_case.py`
  - **Mudanca:** ajustar assinatura para `execute(horse_id: str, owner_id: str, horse_dto: HorseDto) -> HorseDto`, validar ownership com `find_by_id_and_owner_id(...)` e garantir `dto.id = horse_id` antes de reconstruir `Horse`.
  - **Justificativa:** impedir update de cavalo de terceiros e evitar troca indevida de identidade no replace.
  - **Impacto:** `core`

- **Arquivo:** `src/equiny/core/profiling/use_cases/__init__.py`
  - **Mudanca:** exportar `UpdateHorseUseCase` no pacote.
  - **Justificativa:** manter API publica consistente com os demais casos de uso.
  - **Impacto:** `core`

- **Arquivo:** `src/equiny/validation/profiling/horse_schema.py`
  - **Mudanca:** incluir campo `is_active: bool` (com default seguro para compatibilidade) e atualizar `to_dto()` para preencher `HorseDto` completo.
  - **Justificativa:** `HorseDto` exige `is_active`; sem isso o fluxo de update quebra na borda.
  - **Impacto:** `validation`

- **Arquivo:** `src/equiny/database/sqlalchemy/models/profiling/horse_model.py`
  - **Mudanca:** adicionar mapeamento da coluna `is_active`.
  - **Justificativa:** persistir status ativo/inativo alinhado ao dominio.
  - **Impacto:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`
  - **Mudanca:** mapear `is_active` nos sentidos `Model -> DTO` e `Entity -> Model`.
  - **Justificativa:** manter contrato de dados consistente entre dominio e persistencia.
  - **Impacto:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
  - **Mudanca:** implementar `replace(horse: Horse) -> None` e `replace_gallery(horse_id: Id, gallery: Gallery) -> None` conforme contrato `HorsesRepository`.
  - **Justificativa:** o update depende de `replace` e o protocolo ja exige ambos os metodos.
  - **Impacto:** `database`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** exportar `UpdateHorseController`.
  - **Justificativa:** manter padrao de exports dos controllers de `profiling`.
  - **Impacto:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/horses_router.py`
  - **Mudanca:** registrar `UpdateHorseController.handle(router)`.
  - **Justificativa:** expor o endpoint no modulo `horses`.
  - **Impacto:** `routers`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta entrega.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> PUT /profiling/horses/{horse_id}
  -> HorsesRouter
  -> UpdateHorseController
       -> Depends(ProfilingPipe.get_owner)
       -> Depends(DatabasePipe.get_horses_repository)
       -> HorseSchema.to_dto()
  -> UpdateHorseUseCase.execute(horse_id, owner_id, horse_dto)
       -> repository.find_by_id_and_owner_id(...)
       -> Horse.create(dto_com_id_do_path)
       -> repository.replace(horse)
  -> SqlalchemyHorsesRepository
       -> HorsesMapper.to_model(...)
       -> UPDATE horses
  <- HTTP 200 (HorseDto)
```

## 9.2 Referencias internas
- `src/equiny/rest/controllers/profiling/create_horse_controller.py` (padrao de controller com `Schema` + `UseCase`)
- `src/equiny/rest/controllers/profiling/fetch_horse_controller.py` (padrao de rota com `/{horse_id}`)
- `src/equiny/core/profiling/use_cases/create_horse_gallery_use_case.py` (referencia de validacao por ownership com `find_by_id_and_owner_id`)
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py` (repositorio alvo para implementacao de `replace`)

# 10. Status final da implementacao

- Endpoint `PUT /profiling/horses/{horse_id}` implementado e registrado em `HorsesRouter`.
- `UpdateHorseUseCase` consolidado com ownership check e `horse_id` do path como source of truth (`horse_dto.id = horse_id`).
- `HorsesRepository` implementado integralmente na camada SQLAlchemy para `replace(...)` e `replace_gallery(...)`.
- Persistencia de `is_active` concluida em migration Alembic, model SQLAlchemy, mapper e schema de validacao.
- Contrato de resposta mantido em `HorseDto` com `HTTP 200` no update.
