# PRD - Presence (Profiling)

## Objetivo
Permitir consultar e propagar em tempo real o status de presença (`online/offline`) de owners no contexto de profiling.

## Entregas MVP
- Endpoint HTTP `GET /profiling/owners/{owner_id}/presence` para consulta de presença.
- Room WebSocket `WS /profiling/owners/{owner_id}/presence?token=<jwt>` para registro/desregistro e broadcast.
- Persistência de `last_presence_at` no owner para histórico de última presença.

## Regras de negócio
- Presença online é definida pela existência da chave `profiling:owners:presence:{owner_id}` no Redis.
- Apenas owner existente e autenticado pode publicar sua própria presença.
- Em disconnect, a presença é removida do cache e o owner recebe atualização de `last_presence_at`.

## Critérios de aceite
- Consulta HTTP retorna `owner_id` e `is_online`.
- Conexão WebSocket válida marca online e dispara broadcast.
- Desconexão remove presença e dispara broadcast offline.
- Owner inexistente na consulta retorna `404`.
