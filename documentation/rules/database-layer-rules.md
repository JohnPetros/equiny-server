# Regras da camada Database

## Visao geral e modulos da camada

A camada `src/equiny/database/` concentra os adaptadores de persistencia.
No estado atual, ela usa SQLAlchemy para conectar no banco, mapear dados e
implementar contratos de repositorio definidos na camada `core`.

Modulo ativo:

- `sqlalchemy`: implementacao de acesso a dados baseada em SQLAlchemy.

Submodulos principais:

- `sqlalchemy.py`: configuracao de engine/session e acesso a sessao por request.
- `models/`: modelos de banco (tabelas) e base declarativa comum.
- `mappers/`: conversao entre entidade de dominio e modelo ORM.
- `repositories/`: implementacoes concretas das interfaces de repositorio.

## Tooling da Camada de Banco de Dados

### Infraestrutura
- **Ferramenta:** `docker compose`
- **Uso:** Gerenciamento do container de banco de dados PostgreSQL.
- **Comandos principais:**
  - Subir banco: `docker compose up -d postgres`
  - Verificar status: `docker compose ps`

### Migrações (Alembic)
- **Ferramenta:** `alembic` (via `poethepoet`)
- **Regra:** Alterações de esquema DEVEM ser versionadas via migrations. Nunca altere o banco diretamente.
- **Tasks Disponíveis (via `poe`):**
  - `db:migrate "mensagem"`: Gera nova migration com base nas alterações dos modelos.
  - `db:upgrade`: Aplica as migrations pendentes (até `head`).
  - `db:downgrade`: Reverte a última migration aplicada.
  - `db:sync`: Sincroniza a versão do banco sem executar scripts (`alembic stamp`).
  - `db:current`: Exibe a revisão atual do banco.

## Principios Fundamentais

### O que DEVE conter

- Implementacoes concretas de persistencia aderentes aos contratos do `core`.
- Mapeamento explicito entre representacao de banco e tipos de dominio.
- Isolamento de detalhes de SQLAlchemy dentro da camada `database`.
- Gestao de sessao desacoplada dos use cases (injeccao por request).
- Modelo de dados alinhado aos DTOs/entidades que a aplicacao realmente usa.

### O que NUNCA deve conter

- Regras de negocio da aplicacao (isso pertence ao `core`).
- Decisao de fluxo HTTP (status code, body de erro, roteamento).
- Dependencia de controllers/routers para funcionar.
- Serializacao de API diretamente a partir de modelos ORM.
- Commit/rollback manual espalhado por repositorios.

## Glossario arquitetural da camada

### Engine

Objeto de conexao com o banco criado por `create_engine(...)`.
No projeto, a URL e normalizada para `postgresql+psycopg` quando necessario.

### Session

Unidade de trabalho de acesso ao banco.
`SessionLocal` cria sessoes e `Sqlalchemy.get_request_session(...)` recupera a
sessao anexada ao request pelo middleware.

### Model

Representacao ORM de tabela/registro.
`HorseModel` define schema de persistencia e herda campos de auditoria da base `Model`.

### Mapper

Componente de traducao entre tipos de dominio e tipos de persistencia.
`HorsesMapper` converte `HorseModel` para `HorseDto/Horse` e vice-versa.

### Repository

Adaptador que implementa interface de repositorio do dominio usando SQLAlchemy.
`SqlalchemyHorsesRepository` implementa `HorsesRepository` do `core`.

## Padroes de projeto e padroes de uso aplicados

Padroes arquiteturais observados:

- Repository Pattern: repositorio concreto implementa porta do dominio.
- Data Mapper: mapper dedicado para conversao de modelos/entidades.
- Session per Request: sessao criada por request e controlada por middleware.
- Base Repository: classe base para compartilhar dependencia de `Session`.
- Ports and Adapters: camada `database` funciona como adaptador de saida.

Padrao de fluxo atual:

1. Middleware cria `Session` no inicio da request.
2. Controller injeta sessao via `Depends(Sqlalchemy.get_request_session)`.
3. Controller instancia repositorio SQLAlchemy e passa para o use case.
4. Repositorio usa mapper para persistir/buscar entidade de dominio.
5. Middleware aplica commit/rollback e fecha sessao no fim da request.

## Convencoes de nomenclatura

Convencoes observadas e recomendadas:

- Arquivos em `snake_case`.
- Modelos ORM com sufixo `Model` (`HorseModel`).
- Repositorios concretos com prefixo `Sqlalchemy` + sufixo `Repository`.
- Mappers com sufixo `Mapper`.
- Classe de modulo de conexao chamada `Sqlalchemy`.
- Reexport de API publica em `__init__.py` com `__all__`.

Convencao de schema/tabela:

- `__tablename__` em plural (`horses`).
- Chave primaria explicita (`id`).
- Campos de auditoria herdados da base declarativa comum.

## Regras de integracao com outras camadas da aplicacao

### Integracao com Core (`src/equiny/core/`)

- `database` pode importar entidades/DTOs/interfaces do `core` para mapear e implementar portas.
- `core` nunca deve importar `database`.
- Repositorios concretos devem respeitar exatamente assinatura e semantica da interface.

### Integracao com REST (`src/equiny/rest/`)

- Controllers instanciam repositorios concretos com sessao da request.
- REST nao deve acessar modelos ORM diretamente; sempre passar por use case/repository.

### Integracao com Middlewares (`src/equiny/middlewares/`)

- Middleware e dono do ciclo de vida da sessao (open, commit/rollback, close).
- Repositorio assume sessao valida e nao controla transacao global.

### Integracao com Constants/Env (`src/equiny/constants/`)

- URL do banco vem de `ENV.DATABASE_URL`.
- Adaptacoes de driver (postgres/sqlite) devem ficar centralizadas em `sqlalchemy.py`.

Checklist rapido para novas features na camada `database`:

1. Criar/atualizar `Model` para a tabela necessaria.
2. Criar mapper para traducao com tipos do dominio.
3. Implementar repositorio concreto aderente a interface do `core`.
4. Exportar no `__init__.py` do pacote de repositorios.
5. Integrar no controller (injeccao por `Session` de request).
