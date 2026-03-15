# Regras da Camada WebSocket

> 💡 Use este documento ao criar ou revisar fluxo realtime, `channels`, emissao de eventos e integracao de socket com `Redis`.

## Visao Geral

### Resumo da camada

| Aspecto | Diretriz |
|---|---|
| **Objetivo** | Sustentar comunicacao realtime com clientes conectados. |
| **Papel arquitetural** | Ser a borda de entrada e saida de eventos por `WebSocket`. |
| **Entrada principal** | Envelope `{name, payload}` enviado pelo cliente. |
| **Saida principal** | Execucao de `UseCase` e emissao de eventos para sockets ativos. |

### Responsabilidades principais

- Manter o runtime de conexao e emissao em `src/equiny/websocket/`.
- Implementar `channels` por contexto para validar `payload` e delegar execucao ao `core`.
- Integrar o fluxo realtime com o router `WebSocket`, `brokers` `Redis`, cache e `repositories` necessarios ao processamento.

### Limites da camada

- `websocket` e borda de transporte e orquestracao, nao lugar de regra de negocio.
- Pode validar envelope de mensagem, montar `channels` e publicar efeitos realtime, mas nao deve modelar dominio fora do `core`.
- Detalhes de `WebSocket`, sockets conectados e `Redis` nao devem vazar para o `core`.

> ⚠️ Se um `channel` esta decidindo regra de negocio complexa, ele deixou de ser uma borda realtime.

## Estrutura de Diretorios Globais

### Mapa de pastas relevantes

| Caminho | Responsabilidade |
|---|---|
| `src/equiny/websocket/` | Runtime de conexao, desconexao e emissao para sockets ativos. |
| `src/equiny/websocket/channels/` | `Handlers` por contexto que validam `payload` e executam fluxos do dominio. |
| `src/equiny/routers/` | Ponto de entrada do endpoint `WebSocket` e `composition root` do fluxo realtime. |
| `src/equiny/pubsub/redis/` | Distribuicao de eventos para sockets e jobs conectados ao runtime realtime. |

### Regras de organizacao e nomeacao

- `Channels` devem ser agrupados por contexto e seguir convencao `*Channel`.
- Eventos recebidos do cliente devem ser `namespaced` por contexto para permitir roteamento previsivel.
- O runtime de socket deve permanecer centralizado, evitando logica de conexao espalhada pelos `channels`.
- Nao especificar arquivos especificos, pois isso muda constantemente.

## Glossario arquitetural da camada

| Termo | Definicao |
|---|---|
| `Ws Runtime` | Componente que registra sockets conectados, gerencia conexao e emite eventos. |
| `Channel` | Handler por contexto que recebe `name` e `payload`, valida entrada e delega ao dominio. |
| `Event Envelope` | Contrato de entrada enviado pelo cliente: `{name, payload}`. |
| `Socket Key` | Identificador usado para enderecar um socket ou grupo logico de conexoes. |
| `Realtime Broker` | Adaptador que publica eventos para `Redis PubSub` e alimenta a emissao do runtime. |

## Padroes de Projeto

### Padroes arquiteturais aceitos

- **`Channel per Context`** para separar o tratamento realtime por dominio.
- **`Event Envelope`** para padronizar o contrato de entrada do cliente.
- **`Composition Root` no router `WebSocket`** para montar `repositories`, cache e `brokers` por mensagem.
- **Fan-out com `Redis`** para distribuir eventos a sockets conectados sem acoplar o `core` ao transporte.

### Como aplicar os padroes

- O router `WebSocket` deve autenticar, aceitar conexao, validar o envelope recebido e encaminhar o evento para o `channel` correto.
- Cada `channel` deve validar o `payload` com `schema` apropriado, montar o `DTO` necessario e chamar `UseCase.execute(...)`.
- Eventos de saida devem ser publicados por `brokers` apropriados para que o runtime de socket faca a emissao ao cliente.
- O runtime deve ser a unica fonte de verdade sobre sockets ativos e emissao de mensagens.

### Quando evitar

- Nao criar `channel` novo quando o evento ainda pertence ao mesmo contexto e pode ficar coeso no handler existente.
- Nao colocar parse de transporte ou gestao de conexao dentro do `core`.
- Nao pular validacao do envelope ou do `payload` so porque o cliente ja conhece o contrato.

## Regras de Integracao com Outras Camadas

### Mapa de integracao

| Camada | Como integra com `websocket` | Regra |
|---|---|---|
| `core` | Recebe chamadas de `UseCase`, `DTOs`, `errors` e `events` | Nao conhece `WebSocket` nem `Redis`. |
| `database` | Fornece `repositories` concretos montados no `router` | Nao deve vazar `ORM` para `channels`. |
| `pipes` | Pode fornecer auth e acesso a runtime compartilhado | Deve simplificar wiring do fluxo realtime. |
| `pubsub/redis` | Distribui eventos para sockets ativos | Deve manter a entrega desacoplada do dominio. |

### Dependencias permitidas e proibidas

- `websocket` pode depender de `core`, `database`, `providers`, `pipes`, `pubsub/redis` e `FastAPI WebSocket`.
- `websocket` nao deve depender de `controllers` HTTP nem expor classes de transporte ao dominio.

### Contratos de comunicacao

- O cliente deve enviar mensagens no envelope padrao `{name, payload}`.
- `Channels` devem falar com o `core` por `UseCase`, `DTOs`, `interfaces` e `errors` de dominio.
- A emissao realtime deve acontecer por runtime ou `broker` apropriado, nao por acesso direto do `core` ao socket.

## Checklist Rapido para Novas Features na Camada

- [ ] O evento novo possui `namespace` de contexto consistente.
- [ ] O `channel` novo ou alterado valida o `payload` antes de chamar o `UseCase`.
- [ ] O fluxo realtime usa `broker/runtime` para emissao, sem acesso direto do dominio ao socket.
- [ ] O router continua como `composition root` e nao absorveu regra de negocio.
- [ ] O evento emitido para o cliente e serializavel e previsivel.
- [ ] A gestao de sockets continua centralizada em um unico runtime.

## ✅ O que DEVE conter

- Runtime centralizado de conexao e emissao.
- `Channels` por contexto com validacao de `payload`.
- Integracao explicita com `brokers` realtime para fan-out de eventos.
- Envelope de mensagem padronizado.
- Uso do `router WebSocket` como `composition root` do fluxo realtime.

## ❌ O que NUNCA deve conter

- Regra de negocio principal ou acesso direto a `ORM` dentro dos `channels`.
- Emissao de mensagens direto do `core` para o socket sem passar por `broker/runtime`.
- Envelope de mensagem ad hoc sem `namespace` e sem validacao.
- Transporte vazando para o dominio por meio de tipos de `WebSocket` ou `Redis`.
