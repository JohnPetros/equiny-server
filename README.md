<h1 align="center">🐎 Equiny Server</h1>

Backend da plataforma **Equiny**, uma aplicacao de matching para cavalos. Este servico foi desenvolvido em **Python** com **FastAPI**, com foco em regras de negocio desacopladas, arquitetura em camadas e integracoes robustas para autenticacao, feed, match, chat e notificacoes.

## 🚀 Visao Geral

O Equiny Server sustenta os principais fluxos do produto:

-   **Auth e onboarding:** cadastro/login e preparacao inicial do perfil.
-   **Profiling:** gestao de dono, cavalo, galeria de fotos e presenca.
-   **Discovery e matching:** feed com filtros, swipe (like/dislike) e criacao de match.
-   **Messaging:** conversas entre perfis com match e suporte a tempo real.
-   **Eventos assincronos:** processamento orientado a eventos com Inngest e Redis.

## 🛠 Tech Stack

O projeto utiliza uma stack moderna para API, persistencia e mensageria:

-   **Linguagem:** [Python](https://www.python.org/) 3.12+
-   **Framework HTTP:** [FastAPI](https://fastapi.tiangolo.com/)
-   **Servidor ASGI:** [Uvicorn](https://www.uvicorn.org/)
-   **ORM e Persistencia:** [SQLAlchemy](https://www.sqlalchemy.org/) + [PostgreSQL](https://www.postgresql.org/)
-   **Migracoes:** [Alembic](https://alembic.sqlalchemy.org/)
-   **Cache/PubSub:** [Redis](https://redis.io/)
-   **Jobs/Eventos:** [Inngest](https://www.inngest.com/)
-   **Validacao:** [Pydantic](https://docs.pydantic.dev/)
-   **Tooling:** [uv](https://github.com/astral-sh/uv), [Poe the Poet](https://github.com/nat-n/poethepoet), [Ruff](https://docs.astral.sh/ruff/), [Pyright](https://github.com/microsoft/pyright), [Pytest](https://docs.pytest.org/)

## 🏗 Arquitetura

O projeto segue uma arquitetura em camadas inspirada em **Clean Architecture** e **Hexagonal Architecture (Ports and Adapters)**.

### Estrutura de Camadas

-   **Core (`src/equiny/core/`)**: entidades, DTOs, erros de dominio, interfaces e use cases.
-   **Rest (`src/equiny/rest/`)**: controllers HTTP e middlewares de request.
-   **Routers (`src/equiny/routers/`)**: composicao e registro de rotas por contexto.
-   **Pipes (`src/equiny/pipes/`)**: providers de dependencia para `Depends(...)`.
-   **Validation (`src/equiny/validation/`)**: schemas e conversao request/response.
-   **Database (`src/equiny/database/`)**: models, mappers e repositorios SQLAlchemy.
-   **Providers (`src/equiny/providers/`)**: adaptadores externos (JWT, hash, storage, email, push).
-   **PubSub (`src/equiny/pubsub/`)**: orquestracao assincrona por eventos.
-   **WebSocket (`src/equiny/websocket/`)**: comunicacao em tempo real.

Para detalhes tecnicos, consulte a [Documentacao de Arquitetura](documentation/architecture.md).

## 📂 Estrutura do Projeto

```bash
src/equiny/
├── app.py
├── core/
├── rest/
├── routers/
├── pipes/
├── validation/
├── database/
├── providers/
├── pubsub/
└── websocket/
```

## ⚙️ Configuracao e Instalacao

### Pre-requisitos

-   Python 3.12+
-   [uv](https://github.com/astral-sh/uv)
-   Docker e Docker Compose (para Postgres, Redis e Inngest local)

### Passo a passo

1.  **Clone o repositorio:**

    ```bash
    git clone <url-do-repositorio>
    cd equiny-server
    ```

2.  **Configure as variaveis de ambiente:**

    ```bash
    cp .env.example .env
    ```

    Preencha os valores necessarios no arquivo `.env`.

3.  **Suba os servicos de infraestrutura:**

    ```bash
    docker compose up -d
    ```

4.  **Instale as dependencias do projeto:**

    ```bash
    uv sync
    ```

5.  **Aplique as migracoes do banco:**

    ```bash
    uv run poe db:upgrade
    ```

6.  **Execute a API em desenvolvimento:**

    ```bash
    uv run dev
    ```

7.  **(Opcional) Execute o ambiente de eventos local:**

    ```bash
    uv run poe pubsub
    ```

## 📖 Documentacao

Os principais documentos do projeto estao em `documentation/`:

-   [Visao Geral do Produto (overview)](https://raw.githubusercontent.com/JohnPetros/equiny/refs/heads/main/documentation/overview.md)
-   [Arquitetura e Decisoes Tecnicas](documentation/architecture.md)
-   [Regras e Convencoes por Camada](documentation/rules/rules.md)

## 🧪 Testes e Qualidade

Execute os comandos abaixo para validar o projeto:

```bash
uv run poe test
uv run poe typecheck
uv run poe codecheck
```

## 📝 Licenca

Projeto privado da **Equiny**.
