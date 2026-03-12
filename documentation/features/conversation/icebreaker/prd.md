# Icebreaker Conversation Feature PRD

## Objetivo

Gerar uma mensagem inicial (icebreaker) em PT-BR para facilitar o inicio da conversa
entre donos que possuem match no Equiny.

## Escopo do endpoint

- Endpoint: `POST /profiling/icebreaker`
- Autenticacao: JWT obrigatorio
- Entrada:
  - `recipient_owner_id` (ULID)
- Comportamento:
  - `sender_id` e derivado do usuario autenticado
  - workflow recebe IDs de owner (`sender_id` e `recipient_id`)
  - contexto considera dados dos cavalos e matches em comum
- Saida:
  - `201 Created`
  - payload `{ "content": "<icebreaker>" }`

## Regras de negocio

- O caller nao pode definir `sender_id` manualmente.
- O destinatario deve ser referenciado por `recipient_owner_id` valido.
- A geracao deve usar tom natural, curto e amigavel em PT-BR.

## Observacoes de implementacao

- Modelo configurado no agente: Google Gemini (`gemini-2.5-flash`).
- Convencao de evento relacionada: `conversation/icebreaker.sent`.

## Referencias

- Milestone: https://github.com/JohnPetros/equiny/milestone/11
