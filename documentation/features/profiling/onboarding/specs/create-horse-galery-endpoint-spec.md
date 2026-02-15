---
title: Endpoint para criar galeria de imagens do cavalo no onboarding
status: concluido
last_updated_at: 2026-02-15
---

## 1. Objetivo

Entregar o endpoint autenticado `POST /profiling/horses/{horse_id}/gallery` para vincular ao cavalo uma lista ordenada de imagens ja enviadas no fluxo de upload do onboarding. A entrega fecha o fluxo `REST` -> `Core` -> `Database` para persistencia da galeria, reutilizando `CreateHorseGalleryUseCase`, validando o payload e gravando metadados (`key`, `name`, `position`) em tabela dedicada, sem inserir regra de negocio no `controller`.

## 2. Escopo

### 2.1 In-scope

- Criar `Schema` de entrada para lista ordenada de imagens (min 1, max 9).
- Criar endpoint/controller e registrar no `HorsesRouter`.
- Criar persistencia de imagens (`Model`, `Mapper`, `migration`) e implementar `add_many_images(...)`.
- Retornar `GalleryDto` com as imagens na mesma ordem recebida.

### 2.2 Out-of-scope

- Upload de arquivos (feito por endpoint separado em `storage`).
- Remocoes/refactors amplos fora do fluxo de galeria.
- Testes automatizados na `spec`.

## 3. Requisitos

### 3.1 Funcionais

- O endpoint exige `JWT` (via `Depends(AuthPipe.verify_jwt)`).
- Recebe `horse_id` (path param) e body com `images[]`.
- Retorna `HTTP 201` com `GalleryDto`.
- Retorna `HTTP 404` quando `horse_id` nao existir (via `HorseNotFoundError`).

### 3.2 Nao funcionais

- `Controller` permanece magro; persistencia via repositorio; transacao no middleware.
- Ordem da lista e preservada via `position`.

## 4. Regras de negocio e invariantes

- `images` deve ter no minimo 1 item e no maximo 9 itens.
- `key` nao pode repetir dentro do mesmo request.
- A ordem do request define `position` (0..n-1 ou 1..n; padrao deve ser consistente no repositorio/mapper).

## 5. O que ja existe (inventario)

### 5.1 Core (`src/equiny/core/`)

- **`CreateHorseGalleryUseCase`** (`src/equiny/core/profiling/use_cases/create_horse_gallery_use_case.py`) - valida existencia do cavalo e delega persistencia.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - contrato contem `add_many_images(...)`.
- **`Gallery`** (`src/equiny/core/profiling/domain/structures/gallery.py`) - estrutura de dominio que preserva ordem.
- **`Image`** (`src/equiny/core/profiling/domain/structures/image.py`) - estrutura com `key` e `name`.
- **`ImageDto`** (`src/equiny/core/profiling/domain/structures/dtos/image_dto.py`) - contrato recebido da borda.
- **`GalleryDto`** (`src/equiny/core/profiling/domain/structures/dtos/gallery_dto.py`) - contrato de resposta.
- **`HorseNotFoundError`** (`src/equiny/core/profiling/domain/errors/horse_not_found_error.py`) - erro de dominio para `404`.

### 5.2 REST/Controllers e Routers

- **`CreateHorseController`** (`src/equiny/rest/controllers/profiling/create_horse_controller.py`) - referencia de `controller` fino com `Depends(...)`.
- **`FetchHorseController`** (`src/equiny/rest/controllers/profiling/fetch_horse_controller.py`) - referencia de endpoint com `horse_id`.
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - composicao dos endpoints de cavalos.

### 5.3 Pipes

- **`AuthPipe.verify_jwt`** (`src/equiny/pipes/auth_pipe.py`) - dependencia de autenticacao.
- **`DatabasePipe.get_horses_repository`** (`src/equiny/pipes/database_pipe.py`) - injeta repositorio.

### 5.4 Database (SQLAlchemy)

- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - ponto de extensao para `add_many_images(...)`.
- **`HorseModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_model.py`) - tabela `horses` existe (origem de FK).
- **`HorsesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horses_mapper.py`) - referencia de padrao `Domain <-> ORM`.
- **`Model`** (`src/equiny/database/sqlalchemy/models/model.py`) - base declarativa.

### 5.5 Validation

- **`HorseSchema`** (`src/equiny/validation/profiling/horse_schema.py`) - referencia de `Schema` Pydantic.
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - valida `UUID4`.

## 6. O que deve ser criado

### 6.1 REST (Controllers)

- **Arquivo:** `src/equiny/rest/controllers/profiling/create_horse_gallery_controller.py`
  - **Controller:** `CreateHorseGalleryController`
  - **Rota (relativa):** `POST /{horse_id}/gallery`
  - **`status_code`:** `HTTPStatus.CREATED`
  - **`response_model`:** `GalleryDto`
  - **Dependencias:** `Depends(DatabasePipe.get_horses_repository)` e `Depends(AuthPipe.verify_jwt)`

### 6.2 Validation

- **Arquivo:** `src/equiny/validation/profiling/galery_schema.py`
  - **Schema:** `ImageSchema` (reutilizado no body local do controller)
  - **Campos:** `images: list[ImageSchema]` (min 1, max 9)
  - **Observacao:** a validacao de duplicidade de `key` ficou fora desta entrega

### 6.3 Database (SQLAlchemy)

- **Arquivo:** `src/equiny/database/sqlalchemy/models/profiling/horse_image_model.py`
  - **Model:** `HorseImageModel`
  - **Campos:** `id`, `horse_id`, `key`, `name`, `position`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/horse_images_mapper.py`
  - **Mapper:** `HorseImagesMapper`
  - **Conversao:** `Image` + `horse_id` + `position` -> `HorseImageModel`

### 6.4 Alembic (migracoes)

- **Arquivo (novo):** `alembic/versions/<revision>_add_horse_images_table.py`
  - **Mudanca de schema:** criar tabela `horse_images` com FK para `horses.id` e indice por `horse_id`

## 7. O que deve ser modificado

- **Arquivo:** `src/equiny/core/profiling/use_cases/create_horse_gallery_use_case.py`
  - **Mudanca:** retornar `GalleryDto` apos persistir.
  - **Justificativa:** contrato de resposta explicito.
  - **Impacto:** `core`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`
  - **Mudanca:** ajustar nome do argumento para `images` (sem sufixo `_dtos`).
  - **Justificativa:** refletir tipo real (`Image`).
  - **Impacto:** `core`
  - **Compatibilidade:** quebrando (contrato de interface)

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** exportar `CreateHorseGalleryController`.
  - **Justificativa:** padrao de exports.
  - **Impacto:** `rest`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/routers/profiling/horses_router.py`
  - **Mudanca:** registrar `CreateHorseGalleryController.handle(router)`.
  - **Justificativa:** expor endpoint.
  - **Impacto:** `routers`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/validation/profiling/__init__.py`
  - **Mudanca:** exportar `ImageSchema`.
  - **Justificativa:** padrao de exports.
  - **Impacto:** `validation`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
  - **Mudanca:** implementar `add_many_images(...)` com `add_all(...)`, sem `commit`.
  - **Justificativa:** concluir persistencia.
  - **Impacto:** `database`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/database/sqlalchemy/models/profiling/horse_model.py`
  - **Mudanca:** adicionar relacionamento `images` com `HorseImageModel`.
  - **Justificativa:** composicao ORM.
  - **Impacto:** `database`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/database/sqlalchemy/models/profiling/__init__.py`
  - **Mudanca:** exportar `HorseImageModel`.
  - **Justificativa:** padrao de exports.
  - **Impacto:** `database`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/__init__.py`
  - **Mudanca:** exportar `HorseImagesMapper`.
  - **Justificativa:** padrao de exports.
  - **Impacto:** `database`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `alembic/env.py`
  - **Mudanca:** importar `HorseImageModel` para registrar metadata.
  - **Justificativa:** `autogenerate` consistente.
  - **Impacto:** `database`
  - **Compatibilidade:** nao quebrando

## 8. O que deve ser removido

- Foram removidos os artefatos antigos com typo `galery/galary` no `core` e no `rest`.

## 9. Fluxo e diagramas

### 9.1 Fluxo de dados (ASCII)

```text
Mobile App
  -> POST /profiling/horses/{horse_id}/gallery
     Authorization: Bearer <jwt>
     body: images[{ key, name }]
  -> CreateHorseGalleryController
       -> valida horse_id + payload (BodySchema + ImageSchema)
       -> converte para ImageDto[]
  -> CreateHorseGalleryUseCase
       -> repository.find_by_id(horse_id)
       -> Gallery.create(images)
       -> repository.add_many_images(horse_id, gallery.images)
  -> SqlalchemyHorsesRepository
       -> HorseImagesMapper.to_models(...)
       -> INSERT horse_images
  <- HTTP 201 (GalleryDto)
```

### 9.2 Layout (ASCII - contrato do endpoint)

```text
POST /profiling/horses/{horse_id}/gallery

request:
{
  "images": [
    { "key": "images/uuid-1.jpg", "name": "frente.jpg" },
    { "key": "images/uuid-2.jpg", "name": "lateral.jpg" }
  ]
}

response 201:
{
  "images": [
    { "key": "images/uuid-1.jpg", "name": "frente.jpg" },
    { "key": "images/uuid-2.jpg", "name": "lateral.jpg" }
  ]
}
```

### 9.3 Referencias internas

- `src/equiny/rest/controllers/profiling/create_horse_controller.py`
- `src/equiny/rest/controllers/profiling/fetch_horse_controller.py`
- `src/equiny/routers/profiling/horses_router.py`
- `src/equiny/core/profiling/use_cases/create_horse_gallery_use_case.py`
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
- `documentation/features/profiling/onboarding/specs/upload-image-files-spec.md`
