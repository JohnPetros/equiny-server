# Regras da Camada WebSocket

# Visao Geral
- Objetivo da camada
  - Expor um endpoint WebSocket para o cliente enviar eventos (nome + payload) e disparar orquestracao de casos de uso do `core`.
  - Integrar comunicacao em tempo real via `RedisPubSub` + `ws.emit(...)` para entrega de eventos para sockets conectados.
- Responsabilidades principais
  - Aceitar conexoes e manter registro de sockets por `owner_id`: `src/equiny/websocket/ws.py`.
  - Definir o contrato de mensagem recebida (nome + payload) e rotear para o channel correto: `src/equiny/routers/websocket_router.py`.
  - Implementar handlers (channels) por contexto de dominio, validando payload e chamando `UseCase.execute(...)`: `src/equiny/websocket/channels/`.
- Limites da camada
  - A camada `websocket` deve ser **borda/orquestracao**: validar entrada e delegar regra de negocio para `core`.
  - A camada `websocket` nao deve conter regra de negocio, nem modelar entidades de dominio; isso pertence ao `core`.
  - O gerenciamento de sockets deve permanecer encapsulado em `Ws` e nao deve vazar `WebSocket` (FastAPI/Starlette) para o `core`.

# Estrutura de Diretorios Globais
- Mapa de pastas relevantes
  - `src/equiny/websocket/`
  - `src/equiny/websocket/channels/`
  - `src/equiny/routers/websocket_router.py`
  - `src/equiny/pubsub/redis/redis_pubsub.py`
- Responsabilidade de cada diretorio
  - `src/equiny/websocket/`: runtime de conexao/emissao (`ws = Ws()`) e export publico via `__all__`.
  - `src/equiny/websocket/channels/`: handlers por contexto (ex: `ProfilingChannel`, `ConversationChannel`).
  - `src/equiny/routers/websocket_router.py`: endpoint WebSocket, parse de JSON recebido e roteamento para channels.
  - `src/equiny/pubsub/redis/redis_pubsub.py`: adaptador pubsub que consome mensagens Redis e chama `ws.emit(...)`.
- Regras de organizacao e nomeacao
  - Um handler de websocket deve viver em `src/equiny/websocket/channels/` e seguir o padrao `*Channel`.
  - Eventos recebidos do cliente devem ser name-spaced por contexto (padrao atual): `profiling/...` e `conversation/...`: `src/equiny/routers/websocket_router.py`.
  - Exports do pacote devem ser explicitos via `__init__.py` + `__all__`: `src/equiny/websocket/channels/__init__.py`, `src/equiny/websocket/__init__.py`.

# Principios Fundamentais
## Deve conter
- Elementos obrigatorios da camada
  - **Contrato de mensagem**: sempre receber `{ "name": str, "payload": Any }` e validar via schema: `JsonSchema` em `src/equiny/routers/websocket_router.py`.
  - **Validacao de payload** por evento no channel usando `Schema.model_validate(...)` e schemas locais (por handler): `src/equiny/websocket/channels/profiling_channel.py`, `src/equiny/websocket/channels/conversation_channel.py`.
  - **Orquestracao por UseCase**: channel instancia o caso de uso e chama `execute(...)` (sem regra de negocio dentro do handler): `RegisterOwnerPresenceUseCase`, `UnregisterOwnerPresenceUseCase`, `SendMessageUseCase`.
  - **Dependencias por contexto**: repositories e providers sao injetados no constructor do channel (nao buscar globalmente): `src/equiny/websocket/channels/*.py`.
- Praticas recomendadas
  - Manter `handle(...)` com roteamento simples (match/case) e isolar validacao e execucao em metodos privados (padrao atual): `src/equiny/websocket/channels/*_channel.py`.
  - Manter payload schemas pequenos e tipados (ex: `IdSchema`, `Field(default_factory=list)`), para falhar cedo em input invalido.

## Nao deve conter
- Antipadroes e acoplamentos proibidos
  - Channel nao deve conter branching de negocio; qualquer decisao de dominio deve ir para o `core`.
  - Router WebSocket nao deve conter regra de negocio (apenas parse, roteamento, abertura de recursos e delegacao).
  - Nao deve expor SDKs de transporte (FastAPI WebSocket, Redis client) para o `core`.
- Responsabilidades que pertencem a outras camadas
  - Persistencia (models/mappers/queries) pertence a `src/equiny/database/sqlalchemy/`.
  - Contratos HTTP e status codes pertencem a `rest`/`routers` HTTP; WebSocket trata eventos e payload.

# Padroes de Projeto
- Padroes arquiteturais aceitos
  - Clean/Hexagonal: `websocket` como borda; `core` como regra; `database` como adaptador de persistencia; dependencias sempre apontam para dentro (conforme `documentation/architecture.md`).
  - Handler por contexto (channel): o router decide o channel por prefixo do evento e o channel decide a acao por `event_name`.
- Como aplicar cada padrao na camada
  - Router deve:
    - autenticar (padrao atual: `AuthPipe.verify_jwt_from_query`),
    - aceitar socket e registrar em `ws.connect(owner_id, websocket)`,
    - ler JSON e validar com `JsonSchema.model_validate(...)`,
    - criar broker e repositorios, instanciar channel e chamar `channel.handle(name, payload)`: `src/equiny/routers/websocket_router.py`.
  - Channel deve:
    - validar o payload com schema Pydantic (`Schema.model_validate(...)`),
    - instanciar `UseCase` e executar `execute(...)`,
    - publicar efeitos via `Broker` quando aplicavel (dependencia ja injetada).
- Quando evitar cada padrao
  - Nao criar evento novo sem um prefixo de contexto consistente (`profiling/` ou `conversation/`) enquanto o roteamento for baseado em prefixo.
  - Nao mover logica de parse/roteamento para dentro de `core`; transporte e detalhe de borda.

# Padroes de Uso Aplicados
- Fluxos comuns da camada
  - Cliente conecta em `WS /websocket/{owner_id}?token=<jwt>` e envia eventos `{name, payload}`; o server roteia para o channel e executa use case: `src/equiny/routers/websocket_router.py`.
  - Server emite eventos para um socket via `RedisPubSub.reader()` consumindo Redis e chamando `ws.emit(socket_key, event)`: `src/equiny/pubsub/redis/redis_pubsub.py`.
- Exemplos de uso correto
  - Profiling presence:
    - Evento `OwnerEnteredEvent.NAME` com payload `{ owner_id }` chama `RegisterOwnerPresenceUseCase.execute(owner_id)`: `src/equiny/websocket/channels/profiling_channel.py`.
    - Evento `OwnerExitedEvent.NAME` com payload `{ owner_id }` chama `UnregisterOwnerPresenceUseCase.execute(owner_id)`: `src/equiny/websocket/channels/profiling_channel.py`.
  - Conversation send message:
    - Evento `MessageSentEvent.name` com payload `{ message_content, chat_id, sender_id, attachments[] }` chama `SendMessageUseCase.execute(MessageDto(...), chat_id)`: `src/equiny/websocket/channels/conversation_channel.py`.
- Erros comuns e como evitar
  - Enviar `name` sem prefixo conhecido: cai em erro `Event not supported` no router; defina `profiling/...` ou `conversation/...`: `src/equiny/routers/websocket_router.py`.
  - Payload divergente do schema do handler: `Schema.model_validate(...)` falha; mantenha o payload alinhado ao schema do channel.
  - Misturar concerns de DB/transacao no channel: o padrao atual abre sessao no router e passa repositorios para o channel; preserve esse limite.

# Regras de Integracao com Outras Camadas
- Dependencias permitidas e proibidas
  - `websocket` pode depender de:
    - `core` (events, use cases, interfaces, erros de dominio): `src/equiny/websocket/channels/*.py`.
    - `validation` (schemas Pydantic compartilhados): `equiny.validation.shared`.
    - `database` (repositorios concretos SQLAlchemy, instanciados no router): `src/equiny/routers/websocket_router.py`.
    - `pipes` (Depends para auth, providers, database, pubsub): `src/equiny/routers/websocket_router.py`.
  - `websocket` nao deve depender de:
    - detalhes internos de `database` (models/mappers) dentro de channels.
    - `rest/controllers` HTTP para executar logica.
- Contratos/interface de comunicacao
  - Contrato de entrada do cliente: `JsonSchema` com `name` e `payload`: `src/equiny/routers/websocket_router.py`.
  - Contrato de emissao para o socket: `ws.emit(socket_key, event)` com payload JSON-serializavel (via `jsonable_encoder`): `src/equiny/websocket/ws.py`.
  - Integracao com pubsub: `RedisPubSub.publish(socket_key, action, event)` publica no Redis; `reader()` consome e executa `ws.emit(...)`: `src/equiny/pubsub/redis/redis_pubsub.py`.
- Direcao de dependencia e limites de acoplamento
  - `core` nao deve importar `websocket`.
  - `routers/websocket_router.py` pode conhecer implementacoes concretas (repositorios SQLAlchemy, brokers Redis) como composition root do fluxo WebSocket.

| De | Para | Tipo | Contrato | Arquivo real |
|---|---|---|---|---|
| cliente | `WebSocketRouter` | WebSocket | `{name, payload}` | `src/equiny/routers/websocket_router.py` |
| `WebSocketRouter` | `ConversationChannel` | call | `handle(name, payload)` | `src/equiny/websocket/channels/conversation_channel.py` |
| `WebSocketRouter` | `ProfilingChannel` | call | `handle(name, payload)` | `src/equiny/websocket/channels/profiling_channel.py` |
| `RedisPubSub.reader` | `ws` | call | `emit(socket_key, event)` | `src/equiny/pubsub/redis/redis_pubsub.py` |

# Checklist Rapido para Novas Features na Camada
- Itens objetivos de validacao antes de abrir PR
  - Evento novo possui prefixo de contexto suportado pelo router (padrao atual: `profiling/` ou `conversation/`).
  - Channel novo segue `*Channel`, vive em `src/equiny/websocket/channels/` e esta exportado em `src/equiny/websocket/channels/__init__.py`.
  - Handler valida payload com `Schema.model_validate(...)` antes de executar `UseCase`.
  - Channel chama `UseCase.execute(...)` e nao contem regra de negocio.
  - Router abre recursos (sessao SQLAlchemy) e injeta repositorios no channel, sem espalhar transacao para o core.
- Criterios minimos de conformidade arquitetural
  - Nenhum import do `core` aponta para `websocket`.
  - WebSocketRouter permanece como composition root do fluxo (instanciacao de repositorios concretos e brokers).
  - Mensagens emitidas sao JSON-serializaveis (passam por `jsonable_encoder` em `Ws.emit`).
- Sinais de alerta para revisao tecnica
  - Channel com branching de negocio, validacoes de dominio ou regras complexas.
  - Channel acessando ORM models/SQL diretamente.
  - Evento definido sem schema/validacao de payload.
  - Router crescendo com logica que deveria estar no `core` (use case).


