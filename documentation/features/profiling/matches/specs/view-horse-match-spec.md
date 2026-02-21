---
title: Visualizar match de cavalo em Profiling
prd: documentation/features/profiling/matches/prd.md
status: concluído
last_updated_at: 2026-02-19
---

# 1. Objetivo
Entregar o endpoint `GET /profiling/horses/{from_horse_id}/matches/{to_horse_id}` para marcar um match como visualizado pelo cavalo autenticado no contexto de `profiling`, reutilizando o `ViewHorseMatchUseCase` existente e completando a persistencia de estado de visualizacao no `HorsesRepository`, respeitando o fluxo `HTTP -> Router -> Controller -> Pipe/Depends -> UseCase -> Repository -> SQLAlchemy -> PostgreSQL`.

# 2. Escopo

## 2.1 In-scope
- Expor rota HTTP de visualizacao de match no sub-router `profiling/horses`.
- Criar controller dedicado no contexto `profiling` com autenticacao e injecao de `HorsesRepository`.
- Implementar no `SqlalchemyHorsesRepository` os metodos pendentes `find_horse_match_by_to_horse_id(...)` e `replace_horse_match(...)` exigidos por `ViewHorseMatchUseCase`.
- Persistir estado de visualizacao por lado do match (cavalo A e cavalo B) no banco.
- Garantir que o endpoint valide posse do `from_horse_id` pelo `owner` autenticado.

## 2.2 Out-of-scope
- Alterar regras de criacao/remocao de match em `matching` (`swipe` e `dismatch`).
- Alterar contratos do endpoint `GET /profiling/horses/{horse_id}/matches` alem do necessario para manter consistencia de `is_viewed`.
- Introduzir novas regras de notificacao, chat ou eventos assincronos.

# 3. Requisitos

## 3.1 Funcionais
- O endpoint deve aceitar `from_horse_id` e `to_horse_id` no path.
- A requisicao deve exigir JWT valido (`Depends(AuthPipe.verify_jwt)`).
- O caso de uso deve validar que `from_horse_id` pertence ao `owner` autenticado.
- Se o `to_horse_id` nao possuir match relacionado, retornar erro de dominio `HorseMatchNotFoundError` (mapeado para `404`).
- Ao sucesso, o estado de visualizacao do match para o lado de `from_horse_id` deve ser atualizado para `true`.

## 3.2 Nao funcionais
- Manter controller magro: apenas adaptar HTTP e delegar ao `UseCase`.
- Manter `core` sem dependencia de FastAPI/SQLAlchemy.
- Persistencia sem `commit/rollback` no repositorio (controle transacional no middleware).
- Reutilizar contratos e estruturas existentes (`ViewHorseMatchUseCase`, `HorseMatch`, `HorseMatchDto`, `HorsesRepository`).

# 4. Regras de negocio e invariantes
- Um cavalo so pode marcar como visualizado um match que inclua o proprio cavalo (`from_horse_id`) e o cavalo alvo (`to_horse_id`).
- O endpoint nao cria match; apenas atualiza estado de visualizacao de um match existente.
- O `owner` autenticado nao pode visualizar match de um cavalo que nao lhe pertence.
- A atualizacao de visualizacao e idempotente: repetir a chamada mantem estado `true` sem efeitos colaterais adicionais.
- O estado de visualizacao deve ser independente por lado do par (A e B).

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`ViewHorseMatchUseCase`** (`src/equiny/core/matching/use_cases/view_match_use_case.py`) - orquestra validacao de propriedade do cavalo, busca de match e atualizacao para estado visualizado.
- **`HorseMatch`** (`src/equiny/core/profiling/domain/structures/horse_match.py`) - estrutura que encapsula `horse`, `is_viewed` e `created_at`, com metodo `view()`.
- **`HorseMatchNotFoundError`** (`src/equiny/core/profiling/domain/errors/horse_match_not_found_error.py`) - erro de dominio para match inexistente.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - contrato ja define `find_horse_match_by_to_horse_id(...)` e `replace_horse_match(...)`.

## 5.2 Database (`src/equiny/database/`)
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - implementacao concreta de `HorsesRepository`; ainda sem os dois metodos usados por `ViewHorseMatchUseCase`.
- **`MatchModel`** (`src/equiny/database/sqlalchemy/models/matching/match_model.py`) - representa tabela `matches` e precisa suportar estado de visualizacao por lado.
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - representa o cavalo pareado retornado na leitura de match.
- **`HorseMatchesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horse_matches_mapper.py`) - conversao de dados SQL para `HorseMatch`.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`ListHorseMatchesController`** (`src/equiny/rest/controllers/profiling/list_horse_matches_controller.py`) - referencia de endpoint de leitura de matches no mesmo contexto `profiling/horses`.
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - referencia de path com `horse_id` e uso de `AuthPipe`.

## 5.4 Routers (`src/equiny/routers/`)
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - ponto de registro do novo controller no prefixo `/horses`.

## 5.5 Validation (`src/equiny/validation/`)
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - schema para validar IDs de path params.

## 5.6 Pipes e Middlewares
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - valida JWT e fornece payload autenticado.
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - fornece `HorsesRepository` para controllers.
- **`ProfilingPipe`** (`src/equiny/pipes/profiling_pipe.py`) - referencia para obter contexto de owner autenticado quando necessario.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - ciclo de sessao/transacao por request.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/profiling/view_horse_match_controller.py` **(novo arquivo)**
  - **Controller:** `ViewHorseMatchController`
  - **Rota (relativa):** `/{from_horse_id}/matches/{to_horse_id}`
  - **Método HTTP:** `PATCH`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `HorseMatchDto`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(ProfilingPipe.get_owner_id)`, `Depends(DatabasePipe.get_horses_repository)`
  - **Assinatura/contratos:** `def _(from_horse_id: IdSchema, to_horse_id: IdSchema, owner: Owner, repository: HorsesRepository) -> HorseMatchDto`
  - **Fluxo:** receber `owner` do ProfilingPipe -> instanciar `ViewHorseMatchUseCase` -> executar `execute(owner.id.value, from_horse_id, to_horse_id)` -> retornar `HorseMatchDto`.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/database/sqlalchemy/models/matching/match_model.py`
  - **Mudanca:** adicionar colunas booleanas `has_horse_a_viewed` e `has_horse_b_viewed` com default `false` e `nullable=False`.
  - **Justificativa:** persistir visualizacao de match por lado do par, requisito de `HorseMatch.is_viewed`.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
  - **Mudanca:** implementar `find_horse_match_by_to_horse_id(self, to_horse_id: Id) -> HorseMatch | None` e `replace_horse_match(self, from_horse_id: Id, horse_match: HorseMatch) -> None`, incluindo update do campo de visualizacao correto no `MatchModel`.
  - **Justificativa:** completar contrato de `HorsesRepository` e viabilizar execucao do `ViewHorseMatchUseCase`.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/horse_matches_mapper.py`
  - **Mudanca:** ajustar conversao para incluir `is_viewed` explicitamente no `HorseMatchDto`.
  - **Justificativa:** garantir consistencia entre dominio (`HorseMatchDto.is_viewed`) e dados persistidos.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** exportar `ViewHorseMatchController` no pacote.
  - **Justificativa:** manter padrao de API publica de controllers por contexto.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/horses_router.py`
  - **Mudanca:** registrar `ViewHorseMatchController.handle(router)`.
  - **Justificativa:** expor endpoint no modulo correto (`/profiling/horses`).
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`
  - **Mudanca:** ajustar semantica/documentacao dos metodos de match para considerar par (`from_horse_id`, `to_horse_id`) de forma explicita, sem alterar assinatura publica se nao for necessario.
  - **Justificativa:** reduzir ambiguidade no contrato de repositorio para consulta/atualizacao de visualizacao.
  - **Camada:** `core`

- **Arquivo:** `alembic/versions/<nova_revision_view_horse_match>.py` **(novo arquivo gerado por migration, referenciado aqui por impactar schema existente)**
  - **Mudanca:** migration para adicionar colunas de visualizacao em `matches` e backfill seguro (`false`).
  - **Justificativa:** versionar alteracao de schema com Alembic.
  - **Camada:** `database`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta implementacao.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client -> ProfilingRouter -> HorsesRouter -> ViewHorseMatchController
  -> Depends(AuthPipe.verify_jwt) + Depends(ProfilingPipe.get_owner_id) + Depends(DatabasePipe.get_horses_repository)
  -> ViewHorseMatchUseCase.execute(owner_id, from_horse_id, to_horse_id)
  -> HorsesRepository.find_by_id_and_owner_id(from_horse_id, owner_id)
  -> HorsesRepository.find_horse_match_by_to_horse_id(from_horse_id, to_horse_id)
  -> HorsesRepository.replace_horse_match(from_horse_id, to_horse_id, viewed_match)
  -> SqlalchemyHorsesRepository (update MatchModel.has_*_viewed)
  -> HTTP 200 com HorseMatchDto
```

## 9.2 Referencias internas
- `src/equiny/core/matching/use_cases/view_match_use_case.py` (orquestracao ja existente)
- `src/equiny/rest/controllers/profiling/list_horse_matches_controller.py` (padrao de controller no contexto)
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py` (repositorio alvo da implementacao)
- `src/equiny/database/sqlalchemy/models/matching/match_model.py` (schema de persistencia do match)
- `src/equiny/routers/profiling/horses_router.py` (composicao de rotas de horses)
