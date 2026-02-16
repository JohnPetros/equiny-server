---
title: Endpoint de upload de arquivos de imagem no onboarding
status: concluido
last_updated_at: 2026-02-15
---

## 1. Objetivo

Entregar o endpoint autenticado `POST /storage/images/upload` para receber arquivos de imagem via `multipart/form-data`, enviar os arquivos para o Supabase Storage e retornar metadados reutilizaveis na etapa de galeria do onboarding. A entrega adiciona um fluxo completo `REST` -> `Core` -> provider externo (Supabase), com validacoes de entrada, injecao de dependencia via `Pipes` e configuracao por variaveis de ambiente, sem inserir regra de negocio no `controller`.

## 2. Escopo

### 2.1 In-scope

- Criar `StorageRouter` e endpoint `POST /storage/images/upload`.
- Implementar provider Supabase (`FileStorageProvider`).
- Injetar provider via `ProvidersPipe`.
- Retornar lista de `ImageDto` com `key` e `name` (ordem preservada).

### 2.2 Out-of-scope

- Persistencia de imagens no banco (a etapa de galeria cuida disso).
- Testes automatizados na `spec`.

## 3. Requisitos

### 3.1 Funcionais

- O endpoint exige `JWT` (via `Depends(AuthPipe.verify_jwt)`).
- Recebe `files[]` via `multipart/form-data` (min 1 arquivo).
- Realiza upload no bucket configurado e retorna `HTTP 201` com `list[ImageDto]`.

### 3.2 Nao funcionais

- `Controller` magro; sem acesso direto a SDK de Supabase fora do provider.
- Configuracao via `ENV` e `.env.example` atualizado.

## 4. Regras de negocio e invariantes

- Apenas imagens sao aceitas (validar `content_type` como `image/*`).
- A ordem do retorno deve seguir a ordem dos arquivos recebidos.
- `key` retornada deve ser persistivel e reutilizavel no endpoint de galeria.

## 5. O que ja existe (inventario)

### 5.1 Core (Storage)

- **`FileStorageProvider`** (`src/equiny/core/storage/interfaces/file_storage_provider.py`) - contrato de upload unitario e multiplo.
- **`File`** (`src/equiny/core/storage/structures/file.py`) - representa arquivo e pasta alvo.
- **`FileDto`** (`src/equiny/core/storage/structures/dtos/file_dto.py`) - `DTO` para criar `File`.
- **`FileStorageFolder`** (`src/equiny/core/storage/structures/file_storage_folder.py`) - pasta `images` mapeada.

### 5.2 Core (Profiling)

- **`ImageDto`** (`src/equiny/core/profiling/domain/structures/dtos/image_dto.py`) - metadados (`key`, `name`).
- **`CreateHorseGalaryUseCase`** (`src/equiny/core/profiling/use_cases/create_horse_galary_use_case.py`) - consumidor posterior dos metadados.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) - possui `add_many_images(...)` (etapa seguinte).

### 5.3 REST/Routers/Pipes

- **`CreateHorseController`** (`src/equiny/rest/controllers/profiling/create_horse_controller.py`) - referencia de `controller` fino.
- **`HorsesRouter`** (`src/equiny/routers/profiling/horses_router.py`) - referencia de composicao de endpoints.
- **`AuthRouter`** (`src/equiny/routers/auth/auth_router.py`) - referencia de modularizacao por contexto.
- **`AuthPipe.verify_jwt`** (`src/equiny/pipes/auth_pipe.py`) - dependencia de autenticacao.

### 5.4 Config

- **`ProvidersPipe`** (`src/equiny/pipes/providers_pipe.py`) - fabrica de providers.
- **`Env`** (`src/equiny/constants/env.py`) - settings centralizados.
- **`.env.example`** (`.env.example`) - referencia de variaveis locais.
- **`pyproject.toml`** (`pyproject.toml`) - dependencias do servidor.

## 6. O que deve ser criado

### 6.1 Core (Use Cases)

- **Arquivo (novo):** `src/equiny/core/profiling/use_cases/upload_image_files_use_case.py`
  - **Use case:** `UploadImageFilesUseCase`
  - **Entrada:** `list[FileDto]`
  - **Saida:** `list[ImageDto]`
  - **Dependencias:** `FileStorageProvider`
  - **Fluxo:** converter `FileDto` -> `File`, chamar `upload_many(...)`, mapear retorno para `ImageDto`

### 6.2 Providers (Storage/Supabase)

- **Arquivo (novo):** `src/equiny/providers/storage/supabase/supabase_file_storage_provider.py`
  - **Provider:** `SupabaseFileStorageProvider`
  - **Implementa:** `FileStorageProvider`
  - **Config:** `ENV.SUPABASE_URL`, `ENV.SUPABASE_KEY`, `ENV.SUPABASE_STORAGE_BUCKET`

- **Arquivo (novo):** `src/equiny/providers/storage/__init__.py`
- **Arquivo (novo):** `src/equiny/providers/storage/supabase/__init__.py`

### 6.3 REST (Controllers)

- **Arquivo (novo):** `src/equiny/rest/controllers/profiling/upload_image_files_controller.py`
  - **Controller:** `UploadImageFilesController`
  - **Rota (relativa):** `POST /images/upload`
  - **`status_code`:** `HTTPStatus.CREATED`
  - **`response_model`:** `list[ImageDto]`
  - **Dependencias:** `Depends(ProvidersPipe.get_file_storage_provider)`, `Depends(AuthPipe.verify_jwt)`

### 6.4 Routers

- **Arquivo (novo):** `src/equiny/routers/storage/storage_router.py`
  - **Router:** `StorageRouter`
  - **Prefixo:** `/storage`
  - **Controllers:** `UploadImageFilesController.handle(router)`

- **Arquivo (novo):** `src/equiny/routers/storage/__init__.py`

### 6.5 Pipes (Adicionais)

- **Arquivo (novo):** `src/equiny/pipes/storage_pipe.py`
  - **Pipe:** `StoragePipe`
  - **Método:** `get_image_files(files: list[UploadFile]) -> list[FileDto]`
  - **Responsabilidade:** validar Content-Type como imagem e converter `UploadFile` para `FileDto`
  - **Validação:** retorna HTTP 415 (UNSUPPORTED_MEDIA_TYPE) para arquivos não-imagem

- **Arquivo (modificado):** `src/equiny/pipes/__init__.py`
  - **Mudança:** exportar `StoragePipe` no barrel do módulo

## 7. O que deve ser modificado

- **Arquivo:** `src/equiny/core/storage/structures/dtos/file_dto.py`
  - **Mudanca:** adicionar `content_type: str`.
  - **Justificativa:** preservar `MIME type` do upload.
  - **Impacto:** `core`
  - **Compatibilidade:** quebrando

- **Arquivo:** `src/equiny/core/storage/structures/file.py`
  - **Mudanca:** incluir `content_type` na estrutura e no mapeamento `create(...)`/`dto`.
  - **Justificativa:** permitir upload com metadata correta.
  - **Impacto:** `core`
  - **Compatibilidade:** quebrando

- **Arquivo:** `src/equiny/core/profiling/use_cases/__init__.py`
  - **Mudanca:** exportar `UploadImageFilesUseCase`.
  - **Justificativa:** padrao de exports.
  - **Impacto:** `core`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/rest/controllers/profiling/__init__.py`
  - **Mudanca:** exportar `UploadImageFilesController`.
  - **Justificativa:** padrao de exports.
  - **Impacto:** `rest`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/app.py`
  - **Mudanca:** incluir `StorageRouter.register()` via `app.include_router(...)`.
  - **Justificativa:** expor o modulo `storage` desacoplado de `profiling`.
  - **Impacto:** `routers`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/pipes/providers_pipe.py`
  - **Mudanca:** adicionar `get_file_storage_provider()` retornando `SupabaseFileStorageProvider`.
  - **Justificativa:** DI padronizada.
  - **Impacto:** `pipes/middlewares`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `src/equiny/constants/env.py`
  - **Mudanca:** adicionar `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_STORAGE_BUCKET`.
  - **Justificativa:** configuracao via `ENV`.
  - **Impacto:** `core`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `.env.example`
  - **Mudanca:** incluir placeholders das variaveis do Supabase.
  - **Justificativa:** onboarding local.
  - **Impacto:** `core`
  - **Compatibilidade:** nao quebrando

- **Arquivo:** `pyproject.toml`
  - **Mudanca:** adicionar dependencia `supabase`.
  - **Justificativa:** cliente oficial.
  - **Impacto:** `core`
  - **Compatibilidade:** nao quebrando

## 8. O que deve ser removido

- Nao ha remocoes previstas; o escopo e aditivo e de integracao.

## 9. Decisoes de implementacao

### 9.1 Separacao de responsabilidades na validacao

A validacao de `Content-Type` foi dividida em duas camadas:

1. **StoragePipe** (camada REST): realiza validacao preliminar de formato (image/*) e retorna HTTP 415 imediatamente para requisicoes invalidas. Mantem o controller fino e desacoplado de detalhes HTTP.

2. **UploadImageFilesUseCase** (camada Core): revalida as regras de negocio (garantia de que apenas imagens sejam processadas) e levanta `ValidationError` do dominio quando necessario.

Essa separacao segue o principio de fail-fast na borda e dupla-verificacao no core.

### 9.2 Tratamento de erro no provider

O `SupabaseFileStorageProvider` envolve operacoes de upload em bloco `try/except` e converte excecoes do SDK em `AppError` do dominio. Isso:
- Desacopla o core de detalhes do SDK Supabase
- Permite tratamento uniforme de erros via exception handler do FastAPI
- Preserva a cadeia de excecao original via `from error` para debugging

## 10. Fluxo e diagramas

### 10.1 Fluxo de dados (ASCII)

```text
Mobile App
  -> POST /storage/images/upload (multipart: files[])
  -> UploadImageFilesController
       -> StoragePipe.get_image_files(files)
            -> valida Content-Type (image/*)
            -> converte UploadFile[] para FileDto[]
  -> UploadImageFilesUseCase
       -> valida FileDto[] (regras de negocio)
       -> FileStorageProvider.upload_many(files)
  -> SupabaseFileStorageProvider
       -> upload com tratamento de erro (AppError)
       -> Supabase Storage Bucket (images/...)
  <- list[ImageDto] { key, name } (ordem preservada)
Mobile App
  -> usa metadados no endpoint de galeria (vincular ao horse)
```

### 10.2 Layout (ASCII - contrato HTTP da rota)

```text
POST /storage/images/upload
Authorization: Bearer <jwt>
Content-Type: multipart/form-data

request body:
  files[]: image/jpeg | image/png | image/webp

response 201:
  [
    { key: "images/<uuid>-foto-1.jpg", name: "foto-1.jpg" },
    { key: "images/<uuid>-foto-2.png", name: "foto-2.png" }
  ]
```

### 10.3 Referencias internas

- `src/equiny/rest/controllers/profiling/create_horse_controller.py`
- `src/equiny/routers/profiling/horses_router.py`
- `src/equiny/routers/auth/auth_router.py`
- `src/equiny/pipes/providers_pipe.py`
- `src/equiny/core/storage/interfaces/file_storage_provider.py`
- `src/equiny/core/profiling/use_cases/create_horse_galary_use_case.py`
