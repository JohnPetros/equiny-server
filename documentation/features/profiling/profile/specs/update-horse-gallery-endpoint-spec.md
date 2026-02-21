---
title: Atualizacao do endpoint de galeria de cavalo
status: concluida
last_updated_at: 2026-02-16
---

# 1. Objetivo
Entregar o endpoint autenticado `PUT /profiling/horses/{horse_id}/gallery` para substituir a galeria de um cavalo existente, persistindo a nova ordem de imagens no banco, publicando evento de remocao de arquivos obsoletos e executando limpeza assicrona no storage. Tecnicamente, a entrega fecha o fluxo `HTTP` -> `Router` -> `Controller` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL` e adiciona o ramo assicrono `UseCase` -> `Broker` -> `Inngest Job` -> provider de storage.

# 2. Escopo

## 2.1 In-scope
- Criar `controller` para `PUT /{horse_id}/gallery` no contexto de `profiling/horses`.
- Reutilizar `GallerySchema` para entrada e resposta (`to_dto()` -> `GalleryDto`).
- Ajustar `UpdateHorseGalleryUseCase` para garantir autorizacao por owner autenticado.
- Corrigir a identificacao de imagens removidas (diferenca entre galeria antiga e nova).
- Implementar no repositorio SQLAlchemy os metodos `find_gallery_by_horse_id(...)` e `replace_gallery(...)`.
- Criar `job` no Inngest para consumir `profiling/image.files.removed` e remover arquivos do storage.
- Registrar o novo `controller` no `HorsesRouter` e o novo `job` no `InngestPubSub`.

## 2.2 Out-of-scope
- Criar endpoint de leitura da galeria (`GET /{horse_id}/gallery`) nesta entrega.
- Alterar contrato do endpoint de upload (`POST /storage/images/upload`).
- Alterar schema de banco (`horse_images` ja existe), portanto sem nova migration.
- Refactor amplo de nomes legados (`horsers`, `onwer`, etc.) fora do fluxo desta mudanca.

# 3. Requisitos

## 3.1 Funcionais
- O endpoint deve exigir autenticacao via `Depends(ProfilingPipe.get_owner_id)`.
- O endpoint deve receber `horse_id` no path e `GallerySchema` no body.
- O endpoint deve substituir a galeria inteira do cavalo (sem merge parcial).
- O endpoint deve retornar `HTTPStatus.OK` com `GallerySchema` (espelhando a galeria persistida).
- Deve retornar `404` quando cavalo nao existir ou nao pertencer ao owner autenticado.
- Deve publicar evento `ImageFilesRemovedEvent` apenas com chaves realmente removidas da galeria anterior.
- O `job` deve consumir o evento e remover arquivos correspondentes do storage.

## 3.2 Nao funcionais
- `Controller` deve permanecer magro: sem regra de negocio e sem acesso direto a ORM/storage SDK.
- Persistencia deve manter ordenacao por `position` e ocorrer na transacao da request (middleware).
- Publicacao no broker deve ser desacoplada via `PubSubPipe.get_broker`.
- Job deve ser idempotente para listas vazias e tratar erro do provider com `AppError`.

# 4. Regras de negocio e invariantes
- `images` da galeria deve ter entre `1` e `9` itens (ja garantido por `GallerySchema`).
- A ordem do array enviado e a ordem oficial da galeria (`position` sequencial).
- Atualizacao de galeria exige ownership do cavalo (owner autenticado).
- O evento de remocao so inclui arquivos presentes na galeria antiga e ausentes na nova.
- Atualizacao nao deve remover fisicamente arquivos durante a request HTTP; a remocao fisica acontece assicronamente por `job`.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`UpdateHorseGalleryUseCase`** (`src/equiny/core/profiling/use_cases/update_horse_gallery_use_case.py`) - orquestra update de galeria e publicacao de evento; precisa ajuste de ownership e diferenca de imagens.
- **`Gallery`** (`src/equiny/core/profiling/domain/structures/gallery.py`) - estrutura de dominio da galeria, com `dto` e operacoes de diferenca.
- **`ImageFilesRemovedEvent`** (`src/equiny/core/profiling/domain/events/image_files_removed_event.py`) - evento de dominio para limpeza assicrona de arquivos.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - contrato ja declara `find_gallery_by_horse_id(...)` e `replace_gallery(...)`.
- **`Broker`** (`src/equiny/core/shared/interfaces/broker.py`) - porta para publicar eventos.

## 5.2 Database (`src/equiny/database/`)
- **`HorseImageModel`** (`src/equiny/database/sqlalchemy/models/profiling/horse_image_model.py`) - tabela `horse_images` com `horse_id`, `key`, `name`, `position`.
- **`HorseImagesMapper`** (`src/equiny/database/sqlalchemy/mappers/profiling/horse_images_mapper.py`) - converte `Image` para `HorseImageModel` com ordenacao por `position`.
- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) - implementa parte da persistencia de cavalos/galeria; faltam metodos usados pelo use case.

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`CreateHorseGalleryController`** (`src/equiny/rest/controllers/profiling/create_horse_gallery_controller.py`) - referencia de endpoint de galeria com `GallerySchema`.
- **`CreateHorseController`** (`src/equiny/rest/controllers/profiling/create_horse_controller.py`) - referencia de DI com `ProfilingPipe` e `DatabasePipe`.

## 5.4 Routers (`src/equiny/routers/`)
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - composicao dos endpoints de `horses`; ponto de registro do novo `controller`.

## 5.5 Validation (`src/equiny/validation/`)
- **`GallerySchema`** (`src/equiny/validation/profiling/gallery_schema.py`) - valida `images` e converte para `GalleryDto` via `to_dto()`.

## 5.6 Pipes e Middlewares
- **`ProfilingPipe`** (`src/equiny/pipes/profiling_pipe.py`) - resolve owner autenticado (`Depends(AuthPipe.verify_jwt)`).
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) - injeta `HorsesRepository` concreto por request.
- **`PubSubPipe`** (`src/equiny/pipes/pubsub_pipe.py`) - injeta `Broker` concreto (`InngestBroker`).
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - controla `Session` e transacao por request.
- **`HandleInngestClientMiddleware`** (`src/equiny/rest/middlewares/handle_inngest_client_middleware.py`) - injeta `inngest_client` no `request.state`.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.

## 6.1 Core

### 6.1.1 Domain (Entities/Structures/Errors/Events)
- Nenhum novo arquivo de dominio no `core`.

### 6.1.2 Interfaces
- Nenhum novo arquivo de interface no `core`.

### 6.1.3 Use Cases
- Nenhum novo `UseCase` no `core` para o endpoint (reutilizar `UpdateHorseGalleryUseCase`).

## 6.2 Validation
- Nenhum novo schema (reutilizar `GallerySchema` em `src/equiny/validation/profiling/gallery_schema.py`).

## 6.3 Database

### 6.3.1 Models
- Nenhum novo model (reutilizar `HorseImageModel`).

### 6.3.2 Mappers
- Nenhum novo mapper; a extensao fica em `HorseImagesMapper` existente.

### 6.3.3 Repositories
- Nenhum novo repositorio; a implementacao fica em `SqlalchemyHorsesRepository` existente.

### 6.3.4 Migracoes (Alembic)
- **Mudanca de schema:** nenhuma.
- **Nova migration:** nao aplicavel para esta entrega.

## 6.4 Pipes
- Nenhum novo `Pipe` (reutilizar `DatabasePipe`, `ProfilingPipe` e `PubSubPipe`).

## 6.5 REST

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/profiling/update_horse_gallery_controller.py` **(novo arquivo)**
  - **Controller:** `UpdateHorseGalleryController`
  - **Rota (relativa):** `/{horse_id}/gallery`
  - **`status_code`:** `HTTPStatus.OK`
  - **`response_model`:** `GallerySchema`
  - **Dependencias:** `Depends(ProfilingPipe.get_owner_id)`, `Depends(DatabasePipe.get_horses_repository)`, `Depends(PubSubPipe.get_broker)`

## 6.6 Routers
- Nenhum novo router; apenas registrar controller no `HorsesRouter` existente.

## 6.7 PubSub/Jobs
- **Arquivo:** `src/equiny/pubsub/inngest/jobs/profiling/remove_image_files_job.py` **(novo arquivo)**
  - **Job:** `RemoveImageFilesJob`
  - **Trigger:** `TriggerEvent(event=ImageFilesRemovedEvent.name)`
  - **Payload:** `image_files_keys: list[str]`
  - **Responsabilidade:** remover arquivos do bucket de storage com base nas chaves recebidas.
  - **Dependencias:** provider de storage (`FileStorageProvider`/`SupabaseFileStorageProvider`), `Job.sqlalchemy_session()` nao e necessario.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/core/profiling/use_cases/update_horse_gallery_use_case.py`
  - **Mudanca:** incluir `owner_id` no fluxo, validar ownership com `find_by_id_and_owner_id(...)` e publicar evento apenas quando houver chaves removidas.
  - **Justificativa:** evitar update de cavalo de outro owner e reduzir eventos desnecessarios.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/profiling/domain/structures/gallery.py`
  - **Mudanca:** corrigir logica de diferenca para retornar imagens removidas da galeria antiga (`old - new`), nao imagens adicionadas.
  - **Justificativa:** evitar exclusao de arquivos errados no storage.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
  - **Mudanca:** implementar `find_gallery_by_horse_id(...)` (consulta ordenada por `position`) e `replace_gallery(...)` (delete + insert ordenado, sem `commit`).
  - **Justificativa:** cumprir contrato do `HorsesRepository` usado pelo endpoint.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/profiling/horse_images_mapper.py`
  - **Mudanca:** adicionar conversoes auxiliares de `HorseImageModel` para `Image/Gallery` (ou equivalente) para leitura da galeria atual.
  - **Justificativa:** manter o padrao `Data Mapper` na traducao `ORM <-> Domain`.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** exportar `UpdateHorseGalleryController` no `__all__`.
  - **Justificativa:** manter barrel exports estaveis da camada REST.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/routers/profiling/horses_router.py`
  - **Mudanca:** registrar `UpdateHorseGalleryController.handle(router)`.
  - **Justificativa:** expor endpoint no modulo `profiling/horses`.
  - **Camada:** `routers`

- **Arquivo:** `src/equiny/core/profiling/use_cases/__init__.py`
  - **Mudanca:** exportar `UpdateHorseGalleryUseCase` em `__all__`.
  - **Justificativa:** padronizar acesso ao use case por pacote.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/providers/storage/supabase/supabase_file_storage_provider.py`
  - **Mudanca:** implementar `remove_files(folder, file_keys)` para cumprir o contrato atualizado de storage.
  - **Justificativa:** permitir limpeza de arquivos removidos via job de evento.
  - **Camada:** `database`

- **Arquivo:** `src/equiny/core/storage/interfaces/file_storage_provider.py`
  - **Mudanca:** contrato **ja atualizado** com `remove_files(folder: FileStorageFolder, file_keys: list[Text])`.
  - **Justificativa:** manter job desacoplado de SDK especifico e aderente a porta de dominio (confirmar aderencia dos adapters).
  - **Camada:** `core`

- **Arquivo:** `src/equiny/pubsub/inngest/jobs/profiling/__init__.py`
  - **Mudanca:** exportar `RemoveImageFilesJob`.
  - **Justificativa:** manter discoverability dos jobs do contexto `profiling`.
  - **Camada:** `pubsub`

- **Arquivo:** `src/equiny/pubsub/inngest/inngest_pubsub.py`
  - **Mudanca:** registrar `RemoveImageFilesJob.handle(inngest)` na lista de functions.
  - **Justificativa:** ativar processamento assicrono de remocao de arquivos.
  - **Camada:** `pubsub`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nao ha remocoes previstas nesta entrega.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client
  -> PUT /profiling/horses/{horse_id}/gallery
  -> HorsesRouter
  -> UpdateHorseGalleryController
  -> Depends(ProfilingPipe.get_owner_id, DatabasePipe.get_horses_repository, PubSubPipe.get_broker)
  -> UpdateHorseGalleryUseCase
  -> SqlalchemyHorsesRepository.replace_gallery
  -> PostgreSQL (horse_images)
  -> Broker.publish(ImageFilesRemovedEvent)
  -> Inngest (RemoveImageFilesJob)
  -> FileStorageProvider.remove_files
```

## 9.2 Referencias internas
- `src/equiny/rest/controllers/profiling/create_horse_gallery_controller.py`
- `src/equiny/core/profiling/use_cases/update_horse_gallery_use_case.py`
- `src/equiny/core/profiling/domain/structures/gallery.py`
- `src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`
- `src/equiny/database/sqlalchemy/mappers/profiling/horse_images_mapper.py`
- `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`
- `src/equiny/pubsub/inngest/inngest_pubsub.py`
