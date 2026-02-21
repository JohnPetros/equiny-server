---
title: Gerar URLs assinadas para upload de imagens de anexos no chat
prd: documentation/features/storage/chat/prd.md
application: server
status: concluido
last_updated_at: 2026-02-21
---

# 1. Objetivo

Implementar o endpoint `POST /storage/upload/chats/{chat_id}/messages/{message_id}/attachments/{attachment_id}/images` para gerar URLs assinadas de upload de imagens associadas a um anexo de mensagem em um chat especifico. Tecnicamente, a borda REST valida autenticacao e participacao no chat, monta os caminhos canonicos dos arquivos e delega a geracao de signed URLs ao provider de storage.

# 2. O que ja existe?

## Camada REST (Controllers)
- **`GenerateUploadUrlsForAttachmentsController`** (`src/equiny/rest/controllers/storage/generate_attachment_image_upload_url_controller.py`) - Endpoint de geracao de URLs para anexos ja existente e adaptado para o contrato final da spec.

## Camada Pipes
- **`AuthPipe`** (`src/equiny/pipes/auth_pipe.py`) - Garante autenticacao JWT obrigatoria no endpoint.
- **`ConversationPipe`** (`src/equiny/pipes/conversation_pipe.py`) - Valida se o owner autenticado participa do `chat_id` informado na rota.
- **`ProvidersPipe`** (`src/equiny/pipes/providers_pipe.py`) - Injeta `FileStorageProvider` concreto para uso no controller.

## Camada Core (Storage)
- **`FileStorageProvider`** (`src/equiny/core/storage/interfaces/file_storage_provider.py`) - Contrato para gerar URLs assinadas (`generate_upload_urls`).
- **`AttachmentDto`** (`src/equiny/core/storage/structures/dtos/attachment_dto.py`) - Estrutura de dados para compor metadados do anexo e caminho do arquivo.
- **`FileKind`** (`src/equiny/core/storage/structures/file_kind.py`) - Enum/VO com valor `images` para identificar tipo de arquivo.
- **`FileName`** (`src/equiny/core/storage/structures/file_name.py`) - Responsavel por randomizar o nome final do arquivo no path.
- **`UploadUrlDto`** (`src/equiny/core/storage/structures/dtos/upload_url_dto.py`) - Contrato de resposta da URL assinada.

## Camada Providers (Infra)
- **`SupabaseFileStorageProvider`** (`src/equiny/providers/storage/supabase/supabase_file_storage_provider.py`) - Implementacao concreta que chama o Supabase Storage para criar signed upload URLs.

## Camada Routers
- **`StorageRouter`** (`src/equiny/routers/storage/storage_router.py`) - Router do modulo `/storage` onde o controller foi registrado.

# 3. O que deve ser criado?

Nao foi necessario criar novos arquivos. A implementacao foi concluida via adaptacao de arquivos existentes.

# 4. O que deve ser modificado?

## Camada REST (Controllers)
- **Arquivo:** `src/equiny/rest/controllers/storage/generate_attachment_image_upload_url_controller.py`
- **Mudanca:** trocar contrato de `POST /storage/upload/attachments` para `POST /storage/upload/chats/{chat_id}/messages/{message_id}/attachments/{attachment_id}/images`, remover dependencia de use case para este fluxo, receber `files_names` no body, montar paths canonicos e retornar `ListResponse[UploadUrlDto]` com URLs assinadas.

## Camada Routers
- **Arquivo:** `src/equiny/routers/storage/storage_router.py`
- **Mudanca:** garantir registro do `GenerateUploadUrlsForAttachmentsController` no router de storage junto aos demais endpoints de upload.

# 5. O que deve ser removido?

Nenhuma remocao necessaria para concluir esta spec.

# 6. Diagramas e Referencias

- **Fluxo de Dados:**

```text
Client
  -> POST /storage/upload/chats/{chat_id}/messages/{message_id}/attachments/{attachment_id}/images
     -> AuthPipe.verify_jwt
     -> ConversationPipe.verify_chat_participant
     -> GenerateUploadUrlsForAttachmentsController
        -> monta AttachmentDto[] e file_paths[]
        -> FileStorageProvider.generate_upload_urls(file_paths)
           -> SupabaseFileStorageProvider
        <- UploadUrl[]
     <- ListResponse[UploadUrlDto]
```

- **Layout:**

```text
Storage API
`-- /storage
    `-- /upload
        `-- /chats/{chat_id}/messages/{message_id}/attachments/{attachment_id}/images
            `-- body.files_names[] -> signed upload URLs[]
```

- **Referencias:**
  - `src/equiny/rest/controllers/storage/generate_upload_url_for_owner_avatar_controller.py`
  - `src/equiny/rest/controllers/storage/generate_upload_urls_for_horse_gallery_controller.py`
  - `src/equiny/core/storage/use_cases/generate_upload_urls_for_attachments_use_case.py`
