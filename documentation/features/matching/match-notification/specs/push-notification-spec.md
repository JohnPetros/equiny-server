---
title: Notificacao push de match para ambos os owners
prd: documentation/features/matching/match-notification/prd.md
status: concluida
last_updated_at: 2026-03-01
---

# 1. Objetivo
Implementar envio de `push notification` para os dois `owners` quando um `match` for criado e o `HorseMatchNotifiedEvent` for publicado. A versao final adotou orquestracao assíncrona por **Inngest** para notificacao de match e fan-out no broker de profiling (`socket` + `job`) sem alterar contrato HTTP de `swipe`.

# 2. Escopo

## 2.1 In-scope
- Disparar job de notificacao push a partir de `HorseMatchNotifiedEvent` no broker de matching.
- Implementar `SendMatchNotificationJob.handle(payload)` com validacao de payload e chamada do provider de push.
- Reaproveitar `owner_id` do evento para identificar o destinatario do push.
- Criar adaptador concreto de `PushNotificationProvider` em `providers` para envio real.
- Ajustar roteamento de jobs em `RedisPubSub` para acionar o job correto de match.

## 2.2 Out-of-scope
- Criacao de endpoint para cadastro/atualizacao de token de dispositivo.
- Alteracao de regras de negocio de swipe/match (apenas mudanca de orquestracao de evento).
- Garantia de entrega offline (fila duravel, retry com backoff, DLQ).
- Notificacoes de outros dominios (chat, presenca, onboarding).

## 2.3 Riscos
- **Risco de entrega:** falhas no gateway de push podem gerar perda da notificacao sem retry duravel neste ciclo.
- **Risco de contrato:** divergencia entre payload publicado em `HorseMatchNotifiedEvent` e schema do job pode quebrar disparo.
- **Risco operacional:** credenciais invalidas de OneSignal (`Env`) impedem envio em producao.

# 3. Requisitos

## 3.1 Funcionais
- Quando `NotifyHorseMatchUseCase` publicar `HorseMatchNotifiedEvent` para cada lado do match, o sistema deve tentar enviar um push para cada `owner_id`.
- O job de push deve usar dados do `HorseMatchDto` para compor notificacao (nome do cavalo e imagem).
- O envio de push deve ocorrer fora do caminho sincrono da resposta HTTP do `POST /matching/swipes/`.
- O fluxo deve continuar enviando notificacao em tempo real via WebSocket (nao substituir o comportamento atual).

## 3.2 Nao funcionais
- `core` permanece puro, dependendo apenas de `PushNotificationProvider` (interface).
- Job deve ser magro: validar payload, instanciar dependencias e delegar para use case/provider.
- Sem `commit/rollback` no job de push (nao ha transacao DB nesse fluxo).
- Falhas no provider nao devem quebrar o fluxo de request de swipe; devem ser tratadas no contexto do job.

# 4. Regras de negocio e invariantes
- Push de match so pode ser enviado quando existe `HorseMatchNotifiedEvent`.
- Cada match gera duas tentativas de push (uma por owner), respeitando a perspectiva de cada lado.
- `owner_id` do destinatario vem do proprio evento (`HorseMatchNotifiedEvent`).
- Payload minimo para push de match: `owner_id`, `match_horse_name`, `match_horse_image`.
- A entrega push e complementar ao WebSocket; perda de push nao invalida criacao do match.

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`SwipeHorseUseCase`** (`src/equiny/core/matching/use_cases/swipe_horse_use_case.py`) - cria swipe/match e publica `MatchCreatedEvent`.
- **`NotifyHorseMatchUseCase`** (`src/equiny/core/profiling/use_cases/notify_horse_match_use_case.py`) - publica dois `HorseMatchNotifiedEvent` quando o match e encontrado para ambos os lados.
- **`HorseMatchNotifiedEvent`** (`src/equiny/core/profiling/domain/events/horse_match_notified_event.py`) - evento usado hoje para notificacao em tempo real.
- **`PushNotificationProvider`** (`src/equiny/core/notification/interfaces/push_notification_provider.py`) - contrato de envio de push para match.

## 5.2 Database (`src/equiny/database/`)
- Nenhum componente de persistencia e obrigatorio para este ciclo (destinatario resolvido via `owner_id` do evento).

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`SwipeHorseController`** (`src/equiny/rest/controllers/matching/swipe_horse_controller.py`) - ponto de entrada HTTP que aciona o fluxo de criacao de match.

## 5.4 Routers (`src/equiny/routers/`)
- **`SwipesRouter`** (`src/equiny/routers/matching/swipes_router.py`) - registra endpoint de swipe que pode resultar em notificacao.

## 5.5 Validation (`src/equiny/validation/`)
- **`IdSchema`** (`src/equiny/validation/shared/id_schema.py`) - referencia para tipagem/validacao de identificadores em payloads.

## 5.6 Pipes e Middlewares
- **`PubSubPipe`** (`src/equiny/pipes/pubsub_pipe.py`) - injeta `InngestBroker` no fluxo de swipe via `request.state.inngest_client`.
- **`HandleSqlalchemySessionMiddleware`** (`src/equiny/rest/middlewares/handle_sqlalchemy_session_middleware.py`) - mantem o ciclo transacional da request, sem impacto direto no job de push.

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.1 Core

## 6.1.3 Use Cases
- **Arquivo:** `src/equiny/core/notification/use_cases/send_horse_match_push_notification_use_case.py` (**novo arquivo**)
  - **Use case:** `SendHorseMatchPushNotificationUseCase`
  - **Entrada:** `owner_id: str`, `match_horse_name: str`, `match_horse_image: str`
  - **Saida:** `None`
  - **Dependencias:** `PushNotificationProvider`
  - **Fluxo:**
    1. Recebe dados ja validados do job.
    2. Chama `provider.send_horse_match_notification(...)`.
    3. Nao aplica regra de negocio adicional.

- **Arquivo:** `src/equiny/core/notification/use_cases/__init__.py` (**novo arquivo**)
  - **Responsabilidade:** exportar `SendHorseMatchPushNotificationUseCase` via `__all__`.

## 6.7 Providers (Infra)
- **Arquivo:** `src/equiny/providers/notification/onesignal/onesignal_push_notification_provider.py` (**novo arquivo**)
  - **Classe:** `OnesignalPushNotificationProvider`
  - **Responsabilidade:** implementar chamada HTTP para OneSignal usando `owner_id` como `include_aliases.external_id`.
  - **Assinatura/contratos:** implementa `PushNotificationProvider.send_horse_match_notification(owner_id, match_horse_name, match_horse_image)`.
  - **Dependencias:** `httpx`, `equiny.constants.Env`.

- **Arquivo:** `src/equiny/providers/notification/onesignal/__init__.py` (**novo arquivo**)
  - **Responsabilidade:** exportar `OnesignalPushNotificationProvider` via `__all__`.

- **Arquivo:** `src/equiny/providers/notification/__init__.py` (**novo arquivo**)
  - **Responsabilidade:** reexportar `OnesignalPushNotificationProvider` para facilitar consumo em jobs.

## 6.8 PubSub

### 6.8.0 Jobs Inngest
- **Arquivo:** `src/equiny/pubsub/inngest/jobs/profiling/notify_horse_match_job.py` (**modificado**)
  - **Responsabilidade:** escutar `MatchCreatedEvent`, carregar repositorios SQLAlchemy e executar `NotifyHorseMatchUseCase` fora do fluxo HTTP.
  - **Dependencias:** `Inngest`, `Sqlalchemy`, `SqlalchemyHorsesRepository`, `SqlalchemyOwnersRepository`, `RedisProfilingBroker`.

### 6.8.1 Jobs
- **Arquivo:** `src/equiny/pubsub/redis/jobs/notification/send_match_notification_job.py` (**modificado**)
  - **Responsabilidade:** validar payload recebido do evento e delegar envio para `SendHorseMatchPushNotificationUseCase`.
  - **Campos validados:** `owner_id`, `horse_match.owner_horse_name`, `horse_match.owner_horse_image.key`.
  - **Dependencias:** `pydantic`, `OnesignalPushNotificationProvider`, `SupabaseFileStorageProvider`.

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/core/profiling/domain/events/horse_match_notified_event.py`
  - **Mudanca:** garantir exposicao explicita de `owner_id` no payload/evento para consumo do job sem acoplamento a estrutura interna completa do DTO.
  - **Justificativa:** reduzir ambiguidades no roteamento do destinatario do push.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/core/matching/use_cases/swipe_horse_use_case.py`
  - **Mudanca:** troca de orquestracao sincrona de notify por publicacao de `MatchCreatedEvent`.
  - **Justificativa:** desacoplar criacao de match da notificacao, mantendo request HTTP fina e sem I/O adicional.
  - **Camada:** `core`

- **Arquivo:** `src/equiny/pubsub/redis/brokers/redis_profiling_broker.py`
  - **Mudanca:** ao receber `HorseMatchNotifiedEvent`, publicar para socket e para job (`publish_for_job`).
  - **Justificativa:** manter tempo real por WebSocket e habilitar push assíncrono no mesmo evento de dominio.
  - **Camada:** `pubsub`

- **Arquivo:** `src/equiny/pubsub/redis/redis_pubsub.py`
  - **Mudanca:** ajustar dispatch de jobs para rotear `HorseMatchNotifiedEvent.NAME` para `SendMatchNotificationJob.handle(...)` (substituindo filtro atual inconsistente por prefixo/evento errado).
  - **Justificativa:** hoje o job de notificacao nao e acionado pelo evento de match notificado.
  - **Camada:** `pipes/middlewares`

- **Arquivo:** `src/equiny/rest/controllers/matching/swipe_horse_controller.py`
  - **Mudanca:** injecao de broker mudou para `PubSubPipe.get_broker_from_request` (Inngest).
  - **Justificativa:** publicar `MatchCreatedEvent` no broker de jobs assíncronos.
  - **Camada:** `rest`

- **Arquivo:** `src/equiny/pipes/pubsub_pipe.py`
  - **Mudanca:** remoção de `get_redis_matching_broker` e adicao de `get_broker_from_request` para retornar `InngestBroker`.
  - **Justificativa:** alinhar injeção de dependência ao novo fluxo assíncrono de notificacao.
  - **Camada:** `pipes`

- **Arquivo:** `src/equiny/constants/env.py`
  - **Mudanca:** adicionar variaveis de ambiente de push para OneSignal (`ONESIGNAL_APP_ID`, `ONESIGNAL_API_KEY`).
  - **Justificativa:** permitir autenticacao segura na API de push.
  - **Camada:** `core`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- Nenhuma remocao estrutural obrigatoria.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client -> Router -> Controller -> SwipeHorseUseCase -> MatchCreatedEvent -> Inngest
                                                              -> NotifyHorseMatchUseCase
                                                              -> HorseMatchNotifiedEvent
                                                              -> RedisProfilingBroker
                                                                 -> RedisPubSub (socket) -> WebSocket client
                                                                 -> RedisPubSub (job) -> SendMatchNotificationJob -> PushNotificationProvider
```

## 9.2 Referencias internas
- `src/equiny/core/profiling/use_cases/notify_horse_match_use_case.py` (origem da publicacao do evento)
- `src/equiny/core/profiling/domain/events/horse_match_notified_event.py` (evento usado para socket + push)
- `src/equiny/pubsub/inngest/jobs/profiling/notify_horse_match_job.py` (orquestracao assíncrona do match criado)
- `src/equiny/pubsub/redis/brokers/redis_profiling_broker.py` (ponto de fan-out socket/job)
- `src/equiny/pubsub/redis/redis_pubsub.py` (dispatcher de mensagens para socket/job)
- `src/equiny/pubsub/redis/jobs/notification/send_match_notification_job.py` (job alvo da implementacao)
- `src/equiny/core/notification/interfaces/push_notification_provider.py` (contrato do provider de push)

# 10. Implementacao consolidada

- `core/notification`: contrato `PushNotificationProvider` e `SendHorseMatchPushNotificationUseCase` adicionados.
- `providers/notification`: `OnesignalPushNotificationProvider` implementado com `owner_id` como `external_id`.
- `matching`: `SwipeHorseUseCase` publica `MatchCreatedEvent` para processamento assíncrono.
- `profiling`: `NotifyHorseMatchUseCase` passou a resolver owner destinatario explicitamente para cada evento.
- `pubsub`: `NotifyHorseMatchJob` (Inngest) faz orquestracao; `RedisProfilingBroker` publica socket + job; `SendMatchNotificationJob` envia push.
