---
title: Endpoint para buscar galeria de cavalo
status: concluido
last_updated_at: 2026-02-16
---

# 1. Objetivo
Entregar o endpoint `GET /profiling/horses/{horse_id}/gallery` para retornar a galeria de imagens de um cavalo existente, reutilizando o `GetHorseGalleryUseCase` ja presente no `core`. Tecnicamente, a entrega conecta `router` + `controller` + `pipe` + `repository` para completar o fluxo HTTP ate PostgreSQL com resposta tipada e tratamento de erros de dominio (`401`/`404`) sem adicionar regra de negocio nova.

# 2. Escopo

## 2.1 In-scope
- Criar controller REST dedicado para consulta de galeria de cavalo por `horse_id`.
- Registrar o novo controller no `HorsesRouter` para expor `GET /{horse_id}/gallery` sob prefixo de `profiling`.
- Implementar na camada `database` o metodo de leitura da galeria (`find_gallery_by_horse_id`) no `SqlalchemyHorsesRepository`.
- Estender mapper de imagens para conversao `HorseImageModel -> Image/Gallery` mantendo separacao de responsabilidades.
- Reutilizar `GetHorseGalleryUseCase`, `GalleryDto`, `GallerySchema`, `DatabasePipe` e `AuthPipe`.

## 2.2 Out-of-scope
- Criacao/edicao/remocao de imagens da galeria (ja cobertas por outros fluxos).
- Alteracao de regras de onboarding, ownership de cavalo ou matching.
- Refactor de nomenclatura historica (`horsers_repository.py`, `fetch_onwer_controller.py`) fora do necessario para esta entrega.
- Mudancas de schema/migration Alembic.

# 3. Requisitos

## 3.1 Funcionais
- A API deve expor `GET /profiling/horses/{horse_id}/gallery`.
- O endpoint deve exigir autenticacao via `Depends(AuthPipe.verify_jwt)`.
- Em sucesso, deve retornar `HTTPStatus.OK` com payload compativel com `GallerySchema`.
- Se `horse_id` nao existir, deve retornar `404` via `HorseNotFoundError`.
- Se o cavalo existir sem galeria, deve retornar `404` via `GalleryNotFoundError`.

## 3.2 Nao funcionais
- Manter controller fino: somente adaptacao HTTP -> `UseCase` -> HTTP.
- Nao acessar ORM diretamente no controller; consulta deve ocorrer por `HorsesRepository`.
- Preservar padrao de DI do projeto (`DatabasePipe`/`AuthPipe` com `Depends`).
- Garantir ordenacao deterministica da galeria pela coluna `position` na leitura SQLAlchemy.

# 4. Regras de negocio e invariantes
- **Galeria pertence ao cavalo:** a busca de galeria sempre parte de um `horse_id` valido.
- **Falha explicita por inexistencia:** cavalo inexistente e galeria inexistente sao erros distintos de dominio (ambos mapeados para `404`).
- **Contrato da galeria:** resposta contem `images` com `key` e `name`, respeitando o modelo de `GalleryDto`/`GallerySchema`.
- **Autenticacao na borda REST:** sem token valido, o fluxo deve encerrar antes de chegar ao `UseCase`.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`GetHorseGalleryUseCase`** (`src/equiny/core/profiling/use_cases/get_horse_gallery.py`) - orquestra leitura de cavalo e galeria; sera reutilizado sem mudanca de regra.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - ja define o contrato `find_gallery_by_horse_id(...)`.
- **`Gallery` / `GalleryDto` / `Image` / `ImageDto`** (`src/equiny/core/profiling/domain/structures/gallery.py`, `src/equiny/core/profiling/domain/structures/dtos/gallery_dto.py`, `src/equiny/core/profiling/domain/structures/image.py`) - tipos de dominio usados na resposta.

## 5.2 Database (`src/equiny/database/`)
- **`HorseImageModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_image_model.py`) - tabela `horse_images` com `horse_id`, `key`, `name`, `position`.
- **`HorseImagesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horse_images_mapper.py`) - hoje converte `Image -> HorseImageModel` e sera estendido para leitura.
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - implementacao concreta que precisa ganhar consulta de galeria.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - exemplo de endpoint `GET` com `AuthPipe` e `DatabasePipe`.
- **`CreateHorseGalleryController`** (`src/equiny/rest/controllers/profiling/create_horse_gallery_controller.py`) - endpoint no mesmo recurso/path base da galeria.

## 5.4 Routers (`src/equiny/routers/`)
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - compoe endpoints sob `prefix='/horses'`.
- **`ProfilingRouter`** (`src/equiny/routers/profiling/profiling_router.py`) - aplica `prefix='/profiling'` no modulo.

## 5.5 Validation (`src/equiny/validation/`)
- **`GallerySchema`** (`src/equiny/validation/profiling/gallery_schema.py`) - contrato HTTP reutilizavel para `response_model`.

## 5.6 Pipes e Middlewares
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - fornece `HorsesRepository` para o controller.
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - valida token JWT na borda REST.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - garante `Session` por request para repositorios.

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
- **Arquivo:** `src/equiny/rest/controllers/profiling/fetch_horse_gallery_controller.py` (**novo arquivo**)
  - **Controller:** `FetchHorseGalleryController`
  - **Rota (relativa):** `/{horse_id}/gallery`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `GallerySchema`
  - **Dependencias:** `Depends(AuthPipe.verify_jwt)`, `Depends(DatabasePipe.get_horses_repository)`
  - **Responsabilidade:** adaptar requisicao HTTP para `GetHorseGalleryUseCase` e retornar `GalleryDto`.
  - **Assinatura/contratos:** `def _(horse_id: str, repository: HorsesRepository) -> GalleryDto`
  - **Observacoes:** sem logica de negocio e sem acesso direto ao ORM.

## 6.6 Routers
- Nenhum novo arquivo.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** exportar `FetchHorseGalleryController` no import e no `__all__`.
  - **Justificativa:** manter API publica do pacote de controllers consistente.
  - **Impacto:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/horses_router.py`
  - **Mudanca:** registrar `FetchHorseGalleryController.handle(router)`.
  - **Justificativa:** disponibilizar endpoint no modulo de cavalos.
  - **Impacto:** `routers`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
  - **Mudanca:** implementar `find_gallery_by_horse_id(horse_id: Id) -> Gallery | None` com consulta em `HorseImageModel`, filtro por `horse_id` e `order_by(position)`.
  - **Justificativa:** cumprir contrato de `HorsesRepository` usado por `GetHorseGalleryUseCase`.
  - **Impacto:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/horse_images_mapper.py`
  - **Mudanca:** adicionar conversoes de leitura (`HorseImageModel -> Image` e/ou `list[HorseImageModel] -> Gallery`).
  - **Justificativa:** manter traducao de persistencia fora do repositorio e respeitar padrao Data Mapper.
  - **Impacto:** `database`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao prevista nesta entrega.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> GET /profiling/horses/{horse_id}/gallery
  -> ProfilingRouter (/profiling)
  -> HorsesRouter (/horses)
  -> FetchHorseGalleryController (Depends AuthPipe + DatabasePipe)
  -> GetHorseGalleryUseCase.execute(horse_id)
  -> SqlalchemyHorsesRepository.find_by_id(...)
  -> SqlalchemyHorsesRepository.find_gallery_by_horse_id(...)
  -> HorseImagesMapper (Model -> Gallery)
  -> PostgreSQL (horse_images)
  -> GalleryDto -> GallerySchema -> HTTP 200
```

## 9.2 Referencias internas
- `src/equiny/rest/controllers/profiling/fetch_horse_controller.py` (exemplo de `GET` autenticado + `DatabasePipe`)
- `src/equiny/rest/controllers/profiling/create_horse_gallery_controller.py` (mesmo recurso de galeria)
- `src/equiny/routers/profiling/horses_router.py` (ponto de registro do novo controller)
- `src/equiny/core/profiling/use_cases/get_horse_gallery.py` (caso de uso reutilizado)
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py` (repositorio alvo da implementacao)
- `src/equiny/database/sqlalchemy/mappers/profiling/horse_images_mapper.py` (mapper alvo da extensao)
