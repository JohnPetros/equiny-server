# Arquitetura do Projeto

Este documento descreve a arquitetura de software do `equiny-server`, detalhando suas camadas, responsabilidades e o fluxo de dados. O projeto segue princípios de **Clean Architecture** (Arquitetura Limpa) e **Hexagonal Architecture** (Ports and Adapters), visando desacoplamento, testabilidade e manutenção.

## Visão Geral

A arquitetura é dividida em camadas concêntricas, onde a dependência aponta sempre para dentro. O núcleo da aplicação (`Core`) contém a lógica de negócios e é independente de frameworks externos, banco de dados ou interfaces de usuário (API REST).

### Princípios Chave

-   **Independência de Frameworks:** O `core` não depende do FastAPI, SQLAlchemy ou qualquer outra biblioteca externa de infraestrutura.
-   **Testabilidade:** A lógica de negócios pode ser testada unitariamente sem a necessidade de subir banco de dados ou servidor HTTP.
-   **Independência de UI/Database:** A interface web (API REST) e o banco de dados são detalhes de implementação que podem ser trocados sem afetar as regras de negócio.
    -   **Injeção de Dependência:** As dependências são injetadas (geralmente via `Depends` do FastAPI na camada REST), permitindo a inversão de controle.

## Tech Stack

Principais tecnologias e bibliotecas utilizadas no projeto:

-   **Linguagem:** Python 3.12+
-   **Web Framework:** FastAPI
-   **Servidor ASGI:** Uvicorn (via `fastapi[standard]`)
-   **Banco de Dados:** PostgreSQL
-   **Cache:** Redis
-   **ORM:** SQLAlchemy (Síncrono)
-   **Driver Banco de Dados:** Psycopg 3 (`psycopg[binary]`)
-   **Migrações:** Alembic
-   **Gerenciamento de Dependências:** uv
-   **Validação de Dados:** Pydantic
-   **Testes:** Pytest
-   **Qualidade de Código (Lint/Format):** Ruff
-   **Checagem de Tipos:** Pyright
-   **Task Runner:** Poe the Poet
-   **Infraestrutura Local:** Docker Compose

## Estrutura de Diretórios

A estrutura do código em `src/equiny` reflete diretamente a separação em camadas:

```
src/equiny/
├── core/           # Regras de Negócio (Camada mais interna)
│   ├── auth/       # Módulo de Autenticação (Exemplo)
│   │   ├── domain/ # Entidades, Value Objects, Interfaces (Ports)
│   │   └── use_cases/ # Casos de uso da aplicação
│   └── shared/     # Componentes compartilhados do domínio
│
├── database/       # Persistência (Interface Adapter / Infrastructure)
│   └── sqlalchemy/ # Implementação com SQLAlchemy
│       ├── models/ # Modelos do ORM (Tabelas)
│       ├── mappers/ # Conversores Modelo <-> Entidade
│       └── repositories/ # Implementação dos Repositórios
│
├── rest/           # Interface Web (Interface Adapter)
│   └── controllers/# Controladores HTTP (Input/Output)
│
├── routers/        # Configuração de Rotas do FastAPI
│
├── validation/     # Schemas de Validação (Pydantic / DTOs de Entrada/Saída)
│
└── middlewares/    # Middlewares globais (ex: Gestão de Sessão)
```

## Camadas

### 1. Core Layer (`src/equiny/core`)

O coração da aplicação. Contém toda a lógica de negócios.

-   **Responsabilidades:**
    -   Definir entidades de domínio e regras de negócio.
    -   Definir casos de uso (Use Cases) que orquestram as operações.
    -   Definir interfaces (Ports) para repositórios e serviços externos.
-   **Regras:**
    -   **NÃO** deve depender de `rest`, `database`, `fastapi`, `sqlalchemy`.
    -   Deve ser Python puro.
    -   As exceções de domínio devem ser definidas aqui.

### 2. Database Layer (`src/equiny/database`)

Responsável pela persistência dos dados. Atua como um adaptador para o banco de dados.

-   **Responsabilidades:**
    -   Implementar as interfaces de repositório definidas no `core`.
    -   Definir modelos do ORM (SQLAlchemy) que mapeiam para tabelas do banco.
    -   Realizar o mapeamento (Data Mapper) entre Modelos de Banco e Entidades de Domínio.
-   **Regras:**
    -   Depende do `core` (para conhecer as interfaces e entidades).
    -   Não deve conter regras de negócio.
    -   Não deve ser acessada diretamente pela camada `rest` (exceto via injeção de dependência das interfaces).

### 3. REST Layer (`src/equiny/rest` e `src/equiny/routers`)

A interface de entrada da aplicação. Recebe requisições HTTP e entrega respostas.

-   **Responsabilidades:**
    -   **Routers:** Definir as rotas, métodos HTTP e vincular aos controllers.
    -   **Controllers:** Receber dados da requisição, validar (usando schemas), converter para DTOs de domínio, invocar o Use Case apropriado e formatar a resposta.
-   **Regras:**
    -   Depende do `core` (para chamar Use Cases).
    -   Depende de schemas de validação (`src/equiny/validation`).
    -   Não deve conter regras de negócio complexas.
    -   Deve tratar exceções de domínio e convertê-las para respostas HTTP adequadas (Status Codes).

### 4. Validation Layer (`src/equiny/validation`)

Define os contratos de dados para entrada e saída da API (Data Transfer Objects - DTOs).

-   **Responsabilidades:**
    -   Validar dados de entrada (Request Bodies, Query Params) usando Pydantic.
    -   Definir estruturas de resposta (Response Models).

## Fluxo de Dados (Request Lifecycle)

1.  **Request:** O cliente faz uma requisição HTTP.
2.  **Middleware:** A requisição passa por middlewares (ex: `HandleSqlalchemySessionMiddleware` cria a sessão do banco).
3.  **Router:** O FastAPI roteia a requisição para a função de rota correta.
4.  **Controller (`rest`):**
    -   Recebe os dados validados (Pydantic models).
    -   Converte Pydantic models para DTOs/Entidades do Domínio (se necessário).
    -   Solicita a execução de um **Use Case** (`core`).
5.  **Use Case (`core`):**
    -   Recebe entidades/DTOs de domínio.
    -   Aplica regras de negócio.
    -   Interage com **Repositórios** (interfaces) para buscar/salvar dados.
6.  **Repository Implementation (`database`):**
    -   O repositório concreto (injetado) usa o SQLAlchemy.
    -   Converte Entidades de Domínio para Modelos do SQLAlchemy (via Mappers).
    -   Executa queries no banco de dados.
    -   Retorna Entidades de Domínio para o Use Case.
7.  **Response:**
    -   O Use Case retorna o resultado (Entidade/DTO) para o Controller.
    -   O Controller converte o resultado para o Response Model (Pydantic).
    -   O FastAPI serializa e envia a resposta JSON para o cliente.

## PubSub Layer (`src/equiny/pubsub`)

Responsável pela comunicação assíncrona e em tempo real baseada em eventos.

-   **Sub-camadas:**
    -   **`inngest/`** — broker para jobs assíncronos disparados via Inngest (ex: envio de e-mails, push notifications).
    -   **`redis/`** — broker para entrega em tempo real via Redis Pub/Sub → WebSocket.
-   **Brokers Redis (`redis/brokers/`):**
    -   `RedisBroker` — classe base que recebe `RedisPubSub` e implementa o protocolo `Broker`.
    -   `RedisConversationBroker` — roteia `MessageReceivedEvent` para o socket do destinatário.
    -   `RedisProfilingBroker` — roteia eventos de presença para sockets de owners relacionados.
    -   `RedisMatchingBroker` — roteia `HorseMatchNotifiedEvent` para o socket do owner de cada lado do match (via `asyncio.create_task`).
-   **`RedisPubSub` (`redis/redis_pubsub.py`):**
    -   Gerencia conexão Redis com dispatch por `handler`.
    -   `publish_for_socket(socket_key, action, event)` — publica no canal `equiny:socket:{socket_key}`.
    -   `publish_for_job(event)` — publica para jobs internos.
    -   `reader()` — lê mensagens Redis e despacha: `handler == 'socket'` → `ws.emit()`; `handler == 'job'` → jobs internos.
-   **Regras:**
    -   Brokers não devem conter regras de negócio.
    -   Usar `asyncio.create_task` para não bloquear a resposta HTTP.
    -   `core` nunca deve depender de brokers Redis ou Inngest diretamente — apenas do protocolo `Broker`.

## Fluxo WebSocket (Presence)

1.  **Conexão:** Cliente abre `WS /profiling/owners/{owner_id}/presence?token=<jwt>`.
2.  **Room (`websocket/rooms`)**:
    -   Valida JWT via `AuthPipe.verify_jwt_from_query`.
    -   Resolve owner autenticado via `OwnersRepository.find_by_account_id`.
    -   Garante consistência entre `owner_id` da rota e owner do token.
3.  **Use Cases (`core`)**:
    -   `RegisterOwnerPresenceUseCase` grava presença no cache (`CacheProvider`).
    -   `UnregisterOwnerPresenceUseCase` remove presença no disconnect.
4.  **Broadcast:** `Ws.broadcast(...)` publica payload serializável para sockets conectados.

## Fluxo WebSocket (Match Notification)

Quando um swipe gera match, ambos os owners são notificados em tempo real:

1.  **Swipe:** `POST /matching/swipes/` → `SwipeHorseController`.
2.  **Use Case (`core/matching`):** `SwipeHorseUseCase` detecta match via `swipe.verify_match(reverse_swipe)` e publica `MatchCreatedEvent` via `Broker`.
3.  **Job assíncrono (Inngest):** `NotifyHorseMatchJob` escuta `MatchCreatedEvent` e executa `NotifyHorseMatchUseCase(horses_repo, owners_repo, broker)`.
4.  **Notificação de domínio (`core/profiling`):** `NotifyHorseMatchUseCase` busca `HorseMatch` dos dois lados e publica dois `HorseMatchNotifiedEvent` (um por owner destinatário).
5.  **Broker Redis:** `RedisProfilingBroker.publish()` faz fan-out para:
    -   socket (`publish_for_socket`) para tempo real;
    -   job (`publish_for_job`) para push notification.
6.  **Redis:** mensagens publicadas em `equiny:socket:{owner_id}` e `equiny:job:{event_name}`.
7.  **Entrega:** `RedisPubSub.reader()` despacha `handler == 'socket'` para `ws.emit(...)` e `handler == 'job'` para jobs internos (ex: envio de push de match).
8.  **Cliente:** recebe evento `profiling/horse.match.notified` via WebSocket com `HorseMatchDto` perspectivado para o seu lado do match.

> Se o owner não estiver conectado no momento, a notificação é perdida (sem fila de entrega garantida).

## Inversão de Dependência

Para manter o `core` isolado, usamos Inversão de Dependência.
O `core` define a interface (ex: `IUserRepository`). A camada `database` implementa essa interface (`SqlAlchemyUserRepository`).
No `main.py` ou através do sistema de injeção de dependência do FastAPI (`Depends`), a implementação concreta é injetada onde a interface é solicitada.
