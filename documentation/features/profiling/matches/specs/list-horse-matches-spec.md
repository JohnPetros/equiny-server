---
title: Listar matches de um cavalo em Profiling
prd: documentation/features/profiling/matches/prd.md
status: concluida
last_updated_at: 2026-02-18
---

# 1. Objetivo
Entregar o endpoint `GET /profiling/horses/{horse_id}/matches` para retornar os matches de um cavalo no contexto de `profiling`, reutilizando o `ListHorseMatchesUseCase` ja existente e completando a implementacao de persistencia em `HorsesRepository`, mantendo o fluxo padrao `Router -> Controller -> Pipe -> UseCase -> Repository -> SQLAlchemy`.

# 2. Escopo

## 2.1 In-scope
- Expor rota HTTP no modulo `profiling/horses` para listar matches por `horse_id`.
- Criar controller de leitura no contexto `profiling` com `Depends(AuthPipe.verify_jwt)` e `Depends(DatabasePipe.get_horses_repository)`.
- Implementar `find_all_matches(...)` em `SqlalchemyHorsesRepository` com query em `matches` + `horses`.
- Garantir resposta tipada com DTO de `profiling` (`HorseMatchDto`) sem expor `Model` ORM.
- Registrar exports necessarios (`__init__.py`) em `controllers/profiling`.

## 2.2 Out-of-scope
- Alterar regra de negocio de criacao/remocao de match (`matching` context).
- Alterar endpoint existente `GET /matching/matches`.
- Introduzir paginacao/cursor neste endpoint novo (retorno simples em lista).
- Alterar schema de banco ou criar nova migration.

# 3. Requisitos

## 3.1 Funcionais
- O endpoint deve aceitar `horse_id` no path e retornar todos os matches do cavalo.
- Cada item deve conter o cavalo pareado (`horse`) e a data de criacao do match (`created_at`).
- Deve retornar `HTTPStatus.OK` com `response_model=list[HorseMatchDto]`.
- Deve exigir autenticacao JWT no mesmo padrao dos endpoints de `profiling`.

## 3.2 Nao funcionais
- Seguir `Clean Architecture`: controller magro, regra no `core`, persistencia no `database`.
- Reuso de componentes existentes; sem duplicar `UseCase` nem contrato de repositorio.
- Query deve evitar N+1 e trazer os dados necessarios em uma operacao SQL.
- Manter compatibilidade com `Session` por request (sem `commit/rollback` no repositorio).

# 4. Regras de negocio e invariantes
- `horse_id` deve ser valido no formato de `Id` do dominio (`Id.create(...)`).
- O resultado representa matches onde o cavalo aparece em qualquer lado do par (`horse_a_id` ou `horse_b_id`).
- O cavalo retornado em cada item deve ser sempre o "outro" cavalo do match, nunca o proprio `horse_id` da consulta.
- Ordenacao recomendada: `created_at` decrescente para manter consistencia com listagens de matches no sistema.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`ListHorseMatchesUseCase`** (`src/equiny/core/profiling/use_cases/list_horse_matches_use_case.py`) - ja orquestra a leitura chamando `HorsesRepository.find_all_matches(...)`.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - contrato ja possui assinatura `find_all_matches(horse_id: Id) -> list[HorseMatch]`.
- **`HorseMatch`** (`src/equiny/core/profiling/domain/structures/horse_match.py`) - estrutura de dominio para representar match no contexto de `profiling`.
- **`HorseMatchDto`** (`src/equiny/core/profiling/domain/structures/dtos/horse_match_dto.py`) - contrato de saida com `horse` e `created_at`.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - implementacao concreta de `HorsesRepository`; ainda nao implementa `find_all_matches(...)`.
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - modelo ORM de cavalos, usado para montar o `horse` de retorno.
- **`MatchModel`** (`src/equiny/database/sqlalchemy/models/matching/match_model.py`) - modelo ORM da tabela `matches`, com `horse_a_id`, `horse_b_id`, `created_at`.
- **`HorsesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`) - mapeia `HorseModel` para entidade/DTO de cavalo.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`FetchHorseFeedController`** (`src/equiny/rest/controllers/profiling/fetch_horse_feed_controller.py`) - exemplo de endpoint de leitura com `AuthPipe`, `DatabasePipe` e `PaginationResponse`.
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - exemplo de endpoint por `horse_id` no mesmo router `/profiling/horses`.

## 5.4 Routers (`src/equiny/routers/`)
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - sub-router onde o novo controller deve ser registrado.

## 5.5 Validation (`src/equiny/validation/`)
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - alias validado para IDs no path/query.

## 5.6 Pipes e Middlewares
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - fornece `HorsesRepository` via `get_horses_repository`.
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - guard de autenticacao JWT para endpoints protegidos.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - controla ciclo transacional por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.2 Validation
- **Nao ha novo arquivo previsto.** Reutilizar `IdSchema` existente.

## 6.3 Database

### 6.3.2 Mappers
- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/horse_matches_mapper.py` **(novo arquivo)**
  - **Mapper:** `HorseMatchesMapper`
  - **Conversao:** linha de consulta (`HorseModel` pareado + `created_at` do match) `-> HorseMatch`
  - **Dependencias:** `HorseMatch`, `HorseMatchDto`, `HorsesMapper`
  - **Observacoes:** encapsular montagem do DTO para evitar logica de mapeamento no repositorio.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/profiling/list_horse_matches_controller.py` **(novo arquivo)**
  - **Controller:** `ListHorseMatchesController`
  - **Rota (relativa):** `/{horse_id}/matches`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `list[HorseMatchDto]`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(DatabasePipe.get_horses_repository)`
  - **Fluxo:** validar path -> chamar `ListHorseMatchesUseCase.execute(horse_id)` -> mapear para `dto` -> retornar lista.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
  - **Mudanca:** implementar metodo `find_all_matches(self, horse_id: Id) -> list[HorseMatch]`.
  - **Justificativa:** contrato do `HorsesRepository` ja exige esse metodo e o `UseCase` depende dele.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/__init__.py`
  - **Mudanca:** exportar `HorseMatchesMapper` no `__all__`.
  - **Justificativa:** manter API publica de mappers consistente.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** adicionar import/export de `ListHorseMatchesController`.
  - **Justificativa:** seguir padrao de composicao por pacote.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/horses_router.py`
  - **Mudanca:** registrar `ListHorseMatchesController.handle(router)`.
  - **Justificativa:** expor o endpoint no sub-router de `horses` dentro de `profiling`.
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/core/profiling/domain/structures/dtos/__init__.py`
  - **Mudanca:** incluir `HorseMatchDto` no `__all__` (se nao estiver exportado).
  - **Justificativa:** facilitar imports estaveis da camada REST.
  - **Camada:** `core`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta implementacao.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client -> ProfilingRouter -> HorsesRouter -> ListHorseMatchesController
  -> Depends(AuthPipe.verify_jwt)
  -> Depends(DatabasePipe.get_horses_repository)
  -> ListHorseMatchesUseCase
  -> HorsesRepository.find_all_matches
  -> SqlalchemyHorsesRepository (join matches + horses)
  -> HorseMatchesMapper -> HorseMatch -> HorseMatchDto
  -> HTTP 200
```

## 9.2 Referencias internas
- `src/equiny/rest/controllers/profiling/fetch_horse_controller.py` (endpoint por `horse_id` no mesmo contexto)
- `src/equiny/rest/controllers/profiling/fetch_horse_feed_controller.py` (padrao de `Depends` e `response_model`)
- `src/equiny/core/profiling/use_cases/list_horse_matches_use_case.py` (orquestracao ja existente)
- `src/equiny/core/matching/use_cases/list_matches_use_case.py` (referencia de ordenacao por `created_at` em listagem de matches)
- `src/equiny/database/sqlalchemy/repositories/matching/sqlalchemy_matches_repository.py` (exemplo de query em `matches`)

# 10. Decisoes de implementacao

- A consulta de `find_all_matches(...)` foi implementada em uma unica operacao SQL, com `join` entre `matches` e `horses`, usando `case(...)` para selecionar o cavalo pareado em qualquer lado do par.
- A ordenacao final adotada no repositorio foi `MatchModel.created_at.desc()`.
- O mapeamento de linha de consulta para dominio foi centralizado em `HorseMatchesMapper` para manter o repositorio focado em persistencia.
- Foram adicionados testes para `ListHorseMatchesUseCase` e para o endpoint `GET /profiling/horses/{horse_id}/matches` (sucesso e validacao `422`).
- Foi introduzido `HorseMatchFaker` para padronizar massa de teste de `HorseMatch`.
