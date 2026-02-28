---
title: Notificação de match em tempo real via WebSocket
prd: documentation/features/matching/match-notification/prd.md
status: concluída
last_updated_at: 2026-02-28
---

# 1. Objetivo

Implementar notificação em tempo real para ambos os `owners` dos cavalos envolvidos quando um match é criado durante um swipe. A notificação deve ser disparada de forma síncrona dentro do `SwipeHorseUseCase`, compondo internamente o `NotifyHorseMatchUseCase` (contexto `profiling`), publicando um `HorseMatchNotifiedEvent` via `RedisMatchingBroker` para cada lado do match. O evento é entregue ao cliente via WebSocket, chaveado pelo `owner_id`. Push notifications não fazem parte deste escopo.

# 2. Escopo

## 2.1 In-scope

- Modificar `SwipeHorseUseCase` para aceitar `HorsesRepository` e `Broker` como dependências adicionais e, ao detectar match, compor e executar `NotifyHorseMatchUseCase` internamente.
- Modificar `SwipeHorseController` para injetar `HorsesRepository` (via `DatabasePipe`) e `Broker` (via novo método `PubSubPipe.get_redis_matching_broker`) no use case.
- Criar `RedisMatchingBroker` que, ao receber `HorseMatchNotifiedEvent`, publica via `RedisPubSub` para o `owner_id` de cada lado do match.
- Adicionar método `PubSubPipe.get_redis_matching_broker(request)` para obter o `Broker` a partir de `request.app.state.redis_pubsub`.
- Garantir que o fluxo completo `swipe → match → notificação → WebSocket → cliente` funcione de ponta a ponta.

## 2.2 Out-of-scope

- Push notifications (APNs/FCM).
- Criação de `MatchingChannel` (não há eventos inbound de matching via WebSocket).
- Publicação do `MatchCreatedEvent` (evento de domínio do contexto `matching` — não utilizado neste fluxo).
- Alteração de regras de criação/remoção de match (`Swipe.verify_match`, `dismatch`).
- Criação de UI/modal no cliente (responsabilidade do front-end).
- Jobs assíncronos via Inngest para este fluxo.

# 3. Requisitos

## 3.1 Funcionais

- Quando um swipe resulta em match (`swipe.verify_match(reverse_swipe)` retorna `Match`), o sistema deve enviar uma notificação WebSocket para ambos os `owners` dos cavalos envolvidos.
- A notificação deve conter os dados enriquecidos do match (`HorseMatchDto`): `owner_id`, `owner_name`, `owner_avatar`, `owner_horse_id`, `owner_horse_name`, `owner_horse_image`, `owner_location`, `is_viewed`, `created_at`.
- Cada `owner` recebe um `HorseMatchNotifiedEvent` com o `HorseMatchDto` perspectivado para o seu lado do match.
- O evento WebSocket deve ter o nome `'profiling/horse.match.notified'`.
- Se o `owner` não estiver conectado via WebSocket no momento do match, a notificação é perdida (sem fila de entrega garantida — comportamento consistente com o padrão atual do projeto).

## 3.2 Não funcionais

- Manter `core` sem dependência de FastAPI, SQLAlchemy ou Redis.
- A publicação no `RedisMatchingBroker` deve ser assíncrona (`asyncio.create_task`), sem bloquear a resposta HTTP do swipe.
- Manter controller magro: apenas adaptar HTTP e delegar ao `UseCase`.
- O `SwipeHorseUseCase` deve continuar retornando `SwipeDto` sem alteração no contrato de saída.
- Persistência sem `commit`/`rollback` no repositório (controle transacional no middleware).

# 4. Regras de negócio e invariantes

- A notificação só é disparada quando `swipe.verify_match(reverse_swipe)` retorna um `Match` não nulo.
- A notificação é enviada para **ambos** os owners — o owner que realizou o swipe E o owner do cavalo reverso.
- O `NotifyHorseMatchUseCase` busca `HorseMatch` via `HorsesRepository.find_horse_match_by_horses()`. Se o match não for encontrado (cenário de inconsistência), `HorseMatchNotFoundError` é lançado.
- `is_viewed` no `HorseMatchDto` da notificação deve ser `false` (match acabou de ser criado).
- A notificação não altera o fluxo de retorno do swipe: o `SwipeDto` continua sendo retornado ao caller normalmente.
- O `RedisMatchingBroker` deve rotear o evento para o `socket_key` correto, que é o `owner_id` extraído do `HorseMatchDto.owner_id`.

# 5. O que já existe (inventário)

> ⚠️ Apenas itens relevantes para implementar a mudança.

## 5.1 Core (`src/equiny/core/`)

- **`SwipeHorseUseCase`** (`src/equiny/core/matching/use_cases/swipe_horse_use_case.py`) — orquestra criação de swipe e detecção de match. Atualmente aceita apenas `SwipesRepository` e `MatchesRepository`.
- **`NotifyHorseMatchUseCase`** (`src/equiny/core/profiling/use_cases/notify_horse_match_use_case.py`) — busca `HorseMatch` enriquecido para ambos os lados e publica `HorseMatchNotifiedEvent` via `Broker`. Aceita `HorsesRepository` e `Broker`.
- **`HorseMatchNotifiedEvent`** (`src/equiny/core/profiling/domain/events/horse_match_notified_event.py`) — evento com nome `'profiling/horse.match.notified'` e payload contendo `HorseMatchDto`.
- **`MatchCreatedEvent`** (`src/equiny/core/matching/domain/events/match_created_event.py`) — evento de domínio existente mas não publicado em nenhum ponto. Não será utilizado neste fluxo.
- **`Swipe`** (`src/equiny/core/matching/domain/structures/swipe.py`) — possui `verify_match()` que retorna `Match | None` e `become_match()`.
- **`Match`** (`src/equiny/core/matching/domain/structures/match.py`) — structure com `horse_a_id` e `horse_b_id`.
- **`HorseMatch`** (`src/equiny/core/profiling/domain/structures/horse_match.py`) — structure enriquecida com dados do owner/cavalo.
- **`HorseMatchDto`** (`src/equiny/core/profiling/domain/structures/dtos/horse_match_dto.py`) — DTO com `owner_id`, `owner_name`, `owner_avatar`, `owner_horse_id`, `owner_horse_name`, `owner_horse_image`, `owner_location`, `is_viewed`, `created_at`.
- **`HorsesRepository`** (`src/equiny/core/profiling/interfaces/repositories/horsers_repository.py`) — contrato com `find_horse_match_by_horses()`.
- **`Broker`** (`src/equiny/core/shared/interfaces/broker.py`) — Protocol com método `publish(event: Event[Any]) -> None`.

## 5.2 Database (`src/equiny/database/`)

- **`SqlalchemyHorsesRepository`** (`src/equiny/database/sqlalchemy/repositories/profiling/sqlalchemy_horsers_repository.py`) — implementação concreta de `HorsesRepository`, já possui `find_horse_match_by_horses()`.

## 5.3 REST/Controllers (`src/equiny/rest/`)

- **`SwipeHorseController`** (`src/equiny/rest/controllers/matching/swipe_horse_controller.py`) — controller que cria `SwipeHorseUseCase` com `swipes_repo` e `matches_repo` injetados via `Depends`.

## 5.4 PubSub/Redis (`src/equiny/pubsub/`)

- **`RedisBroker`** (`src/equiny/pubsub/redis/brokers/redis_broker.py`) — classe base que recebe `RedisPubSub` no construtor e implementa `Broker`.
- **`RedisConversationBroker`** (`src/equiny/pubsub/redis/brokers/redis_conversation_broker.py`) — implementação de referência que roteia `MessageReceivedEvent` para os sockets corretos via `create_task`.
- **`RedisProfilingBroker`** (`src/equiny/pubsub/redis/brokers/redis_profiling_broker.py`) — implementação de referência que roteia eventos de presença para sockets de owner matches.
- **`RedisPubSub`** (`src/equiny/pubsub/redis/redis_pubsub.py`) — gerencia conexão Redis com dispatch por `handler`: `'socket'` (delega para `_handle_socket` → `ws.emit()`) e `'job'` (delega para `_handle_job` → jobs internos). Expõe `publish_for_socket(socket_key, action, event)` e `publish_for_job(event)` como métodos de publicação.
- **`NotifyMatchJob`** (`src/equiny/pubsub/redis/jobs/notification/notify_match_job.py`) — stub de job para notificação de match via `publish_for_job`. Não é utilizado neste fluxo (esta spec usa o caminho `publish_for_socket`).

## 5.5 Pipes (`src/equiny/pipes/`)

- **`PubSubPipe`** (`src/equiny/pipes/pubsub_pipe.py`) — possui `get_broker_from_request(request)` (retorna `InngestBroker`) e `get_redis_pubsub_from_websocket(websocket)` (retorna `RedisPubSub`).
- **`DatabasePipe`** (`src/equiny/pipes/database_pipe.py`) — possui `get_horses_repository()` que retorna `HorsesRepository`.

## 5.6 WebSocket (`src/equiny/websocket/`)

- **`Ws`** (`src/equiny/websocket/ws.py`) — singleton que gerencia conexões WebSocket em dict `{owner_id: WebSocket}` com métodos `emit()`, `connect()`, `disconnect()`.

# 6. O que deve ser criado

> 🛠️ Arquivos novos por camada. Para cada arquivo: **assinatura**, **responsabilidade** e **dependências**.

## 6.1 PubSub

### 6.1.1 Brokers

- **Arquivo:** `src/equiny/pubsub/redis/brokers/redis_matching_broker.py` **(novo arquivo)**
  - **Classe:** `RedisMatchingBroker(RedisBroker)`
  - **Responsabilidade:** receber eventos do contexto de matching e publicá-los via `RedisPubSub` para os sockets corretos.
  - **Dependências:** `RedisBroker`, `RedisPubSub`, `HorseMatchNotifiedEvent`, `asyncio.create_task`.
  - **Método `publish(self, event: Event[Any]) -> None`:**
    - Verifica se o evento é instância de `HorseMatchNotifiedEvent`.
    - Se sim, delega para `_publish_horse_match_notified_event(event)`.
  - **Método `_publish_horse_match_notified_event(self, event: HorseMatchNotifiedEvent) -> None`:**
    - Extrai `owner_id` de `event.payload.horse_match.owner_id`.
    - Chama `create_task(self.pubsub.publish_for_socket(socket_key=owner_id, action='emit', event=event))`.
  - **Referência de implementação:** `RedisConversationBroker` (`src/equiny/pubsub/redis/brokers/redis_conversation_broker.py`).

**Pseudocódigo:**

```python
class RedisMatchingBroker(RedisBroker):
    def publish(self, event: Event[Any]) -> None:
        if isinstance(event, HorseMatchNotifiedEvent):
            self._publish_horse_match_notified_event(event)

    def _publish_horse_match_notified_event(
        self, event: HorseMatchNotifiedEvent
    ) -> None:
        create_task(
            self.pubsub.publish_for_socket(
                socket_key=event.payload.horse_match.owner_id,
                action='emit',
                event=event,
            )
        )
```

> **Nota:** `NotifyHorseMatchUseCase` chama `broker.publish()` duas vezes — uma para cada lado do match — cada vez com um `HorseMatchNotifiedEvent` contendo o `HorseMatchDto` perspectivado para aquele `owner`. Portanto, `RedisMatchingBroker._publish_horse_match_notified_event` é invocado duas vezes, cada uma publicando para o `owner_id` correto.

# 7. O que deve ser modificado

> ⚠️ Apenas arquivos existentes. Mudanças em arquivos novos ficam na seção 6.

- **Arquivo:** `src/equiny/core/matching/use_cases/swipe_horse_use_case.py`
  - **Mudança:** adicionar `HorsesRepository` e `Broker` como dependências no `__init__`. No bloco de detecção de match (após `self._matches_repository.add(match)`), compor e executar `NotifyHorseMatchUseCase(horses_repository, broker).execute(match.horse_a_id.value, match.horse_b_id.value)`.
  - **Justificativa:** disparar notificação em tempo real para ambos os owners no momento exato da criação do match, dentro do mesmo fluxo síncrono.
  - **Camada:** `core`
  - **Pseudocódigo do `__init__` modificado:**
    ```python
    def __init__(
        self,
        swipes_repository: SwipesRepository,
        matches_repository: MatchesRepository,
        horses_repository: HorsesRepository,
        broker: Broker,
    ) -> None:
        self._swipes_repository = swipes_repository
        self._matches_repository = matches_repository
        self._horses_repository = horses_repository
        self._broker = broker
    ```
  - **Pseudocódigo do bloco de match no `execute`:**
    ```python
    if reverse_swipe is not None:
        match = swipe.verify_match(reverse_swipe)
        if match is not None:
            self._matches_repository.add(match)
            NotifyHorseMatchUseCase(
                self._horses_repository, self._broker
            ).execute(
                match.horse_a_id.value,
                match.horse_b_id.value,
            )
            swipe = swipe.become_match()
    ```

- **Arquivo:** `src/equiny/rest/controllers/matching/swipe_horse_controller.py`
  - **Mudança:** adicionar injeção de `HorsesRepository` via `Depends(DatabasePipe.get_horses_repository)` e `Broker` via `Depends(PubSubPipe.get_redis_matching_broker)`. Passar ambos ao construtor de `SwipeHorseUseCase`.
  - **Justificativa:** fornecer as novas dependências do use case via dependency injection do FastAPI.
  - **Camada:** `rest`
  - **Pseudocódigo do handler modificado:**
    ```python
    def _(
        body: SwipeSchema,
        _: dict[str, str] = Depends(AuthPipe.verify_jwt),
        swipes_repo: SwipesRepository = Depends(DatabasePipe.get_swipes_repository),
        matches_repo: MatchesRepository = Depends(
            DatabasePipe.get_matches_repository
        ),
        horses_repo: HorsesRepository = Depends(
            DatabasePipe.get_horses_repository
        ),
        broker: Broker = Depends(PubSubPipe.get_redis_matching_broker),
    ) -> SwipeDto:
        use_case = SwipeHorseUseCase(
            swipes_repo, matches_repo, horses_repo, broker
        )
        return use_case.execute(body.to_dto())
    ```

- **Arquivo:** `src/equiny/pipes/pubsub_pipe.py`
  - **Mudança:** adicionar método estático `get_redis_matching_broker(request: Request) -> Broker` que obtém `redis_pubsub` de `request.app.state.redis_pubsub` e retorna `RedisMatchingBroker(redis_pubsub)`.
  - **Justificativa:** fornecer `Broker` concreto para o contexto de matching via dependency injection, seguindo o padrão da camada de pipes.
  - **Camada:** `pipes`
  - **Pseudocódigo:**
    ```python
    @staticmethod
    def get_redis_matching_broker(request: Request) -> Broker:
        redis_pubsub = request.app.state.redis_pubsub
        return RedisMatchingBroker(redis_pubsub)
    ```

- **Arquivo:** `src/equiny/pubsub/redis/brokers/__init__.py`
  - **Mudança:** adicionar import e export de `RedisMatchingBroker`.
  - **Justificativa:** manter padrão de API pública de brokers por contexto.
  - **Camada:** `pubsub`
  - **Conteúdo esperado:**
    ```python
    from .redis_conversation_broker import RedisConversationBroker
    from .redis_matching_broker import RedisMatchingBroker
    from .redis_profiling_broker import RedisProfilingBroker

    __all__ = ['RedisConversationBroker', 'RedisMatchingBroker', 'RedisProfilingBroker']
    ```

# 8. O que deve ser removido

> ⚠️ Remoções precisam ser justificadas e seguras (sem quebrar imports/public API).

- Nenhuma remoção prevista nesta implementação.

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)

```text
Client  ──POST /matching/swipes/──>  MatchingRouter
  └──>  SwipeHorseController
        ├── Depends(AuthPipe.verify_jwt)
        ├── Depends(DatabasePipe.get_swipes_repository)    → SwipesRepository
        ├── Depends(DatabasePipe.get_matches_repository)   → MatchesRepository
        ├── Depends(DatabasePipe.get_horses_repository)    → HorsesRepository
        └── Depends(PubSubPipe.get_redis_matching_broker)  → Broker (RedisMatchingBroker)
              │
              └──>  SwipeHorseUseCase.execute(swipe_dto)
                    ├── Swipe.create(dto)
                    ├── swipes_repository.find_by_horses(from, to)  → valida duplicata
                    ├── swipes_repository.find_by_horses(to, from)  → busca swipe reverso
                    ├── swipe.verify_match(reverse_swipe)           → Match | None
                    │
                    ├── [SE MATCH]:
                    │   ├── matches_repository.add(match)
                    │   ├── NotifyHorseMatchUseCase(horses_repo, broker).execute(horse_a_id, horse_b_id)
                    │   │   ├── horses_repo.find_horse_match_by_horses(a, b) → HorseMatch (lado A)
                    │   │   ├── horses_repo.find_horse_match_by_horses(b, a) → HorseMatch (lado B)
                    │   │   ├── broker.publish(HorseMatchNotifiedEvent(horse_a_match.dto))
                    │   │   └── broker.publish(HorseMatchNotifiedEvent(horse_b_match.dto))
                    │   └── swipe.become_match()
                    │
                    ├── swipes_repository.add(swipe)
                    └── return swipe.dto  → HTTP 201 SwipeDto
```

## 9.2 Fluxo de entrega via WebSocket (ASCII)

```text
RedisMatchingBroker.publish(HorseMatchNotifiedEvent)
  └── asyncio.create_task(
        redis_pubsub.publish_for_socket(
            socket_key=owner_id,         ← extraído de HorseMatchDto.owner_id
            action='emit',
            event=HorseMatchNotifiedEvent
        )
      )
      │
      └── Redis PUB  ──equiny:socket:{owner_id}──>  Redis SUB
            │
            └── RedisPubSub.reader()
                  ├── parse message → data['handler'] == 'socket'
                  ├── _handle_socket(data)
                  │     ├── action == 'emit'
                  │     └── ws.emit(socket_key=owner_id, event=parsed_event)
                  │
                  └── WebSocket.send_json({name, payload})  ──>  Client
```

## 9.3 Referências internas

- `src/equiny/core/matching/use_cases/swipe_horse_use_case.py` — use case alvo da modificação principal.
- `src/equiny/core/profiling/use_cases/notify_horse_match_use_case.py` — use case de notificação composto internamente.
- `src/equiny/rest/controllers/matching/swipe_horse_controller.py` — controller alvo de modificação para injeção de dependências.
- `src/equiny/pipes/pubsub_pipe.py` — pipe alvo de modificação para novo método de broker.
- `src/equiny/pubsub/redis/brokers/redis_conversation_broker.py` — referência de implementação de broker.
- `src/equiny/pubsub/redis/redis_pubsub.py` — infraestrutura de publicação e leitura Redis.
- `src/equiny/websocket/ws.py` — entrega final via WebSocket.
