# Regras da Camada Database

> 💡 Use este documento ao criar ou revisar `models`, `mappers`, `repositories`, sessao SQLAlchemy e integracoes de persistencia em `src/equiny/database/`.

## Visao Geral

### Resumo da camada

| Aspecto | Diretriz |
|---|---|
| **Objetivo** | Implementar a persistencia da aplicacao e isolar detalhes de `SQLAlchemy`. |
| **Papel arquitetural** | Ser o adaptador de saida responsavel por banco, `session`, `models` e traducao para o dominio. |
| **Entrada principal** | Contratos definidos pelo `core`. |
| **Saida principal** | `repositories` concretos e tipos de dominio reconstruidos a partir da persistencia. |

### Responsabilidades principais

- Definir `models` ORM, `mappers` e `repositories` concretos aderentes ao `core`.
- Centralizar `engine`, `Session`, `context manager` e bootstrap de acesso ao banco.
- Sustentar `seeders` e operacoes de persistencia sem contaminar as camadas de entrada com detalhes de `SQL`.

### Limites da camada

- Pode depender de `SQLAlchemy`, configuracao de banco e tipos do `core` usados no mapeamento.
- Nao deve concentrar regra de negocio, `status code`, contrato HTTP, composicao de rota ou validacao de transporte.
- Nao deve expor `models` ORM diretamente para `rest`, `websocket` ou clientes externos.

> ⚠️ Se uma decisao funcional importante esta em `repository`, ela provavelmente deveria estar em um `UseCase` do `core`.

## Estrutura de Diretorios Globais

### Mapa de pastas relevantes

| Caminho | Responsabilidade |
|---|---|
| `src/equiny/database/sqlalchemy/` | Infraestrutura principal de persistencia e utilitarios de acesso. |
| `src/equiny/database/sqlalchemy/models/` | `Models` ORM organizados por contexto. |
| `src/equiny/database/sqlalchemy/mappers/` | Conversao entre persistencia e tipos do dominio. |
| `src/equiny/database/sqlalchemy/repositories/` | Implementacoes concretas das `interfaces` do `core`. |
| `src/equiny/database/sqlalchemy/seeders/` | Carga controlada de dados para desenvolvimento e suporte. |

### Regras de organizacao e nomeacao

- A organizacao deve acompanhar os `bounded contexts` do projeto, como `auth`, `profiling`, `matching` e `conversation`.
- `Models`, `mappers` e `repositories` devem permanecer separados por responsabilidade.
- `Repositories` concretos devem usar prefixo de tecnologia, como `Sqlalchemy*Repository`.
- Nao especificar arquivos especificos, pois isso muda constantemente.

## Glossario arquitetural da camada

| Termo | Definicao |
|---|---|
| `Engine` | Conexao base com o banco, criada e reutilizada pela camada. |
| `Session` | Unidade de trabalho transacional usada por `request`, job ou fluxo realtime. |
| `Model` | Representacao ORM do schema persistido. |
| `Mapper` | Tradutor entre `Model` e tipos do `core`. |
| `Repository` | Adaptador concreto que implementa uma `interface` do dominio. |
| `Seeder` | Utilitario para preparar dados em ambientes controlados. |

## Padroes de Projeto

### Padroes arquiteturais aceitos

- **`Repository Pattern`** para implementar portas do dominio.
- **`Data Mapper`** para separar conversao de persistencia da logica de consulta.
- **`Session per Request` / `Session per Scope`** para controlar o ciclo transacional fora do `repository`.
- **`Ports and Adapters`** para manter `database` como adaptador de saida do `core`.

### Como aplicar os padroes

- Cada `repository` deve implementar apenas a semantica definida pela `interface` do `core`.
- Conversoes entre `ORM` e dominio devem passar por `mapper` dedicado ou estrategia equivalente centralizada.
- A `session` deve ser recebida de fora da camada: `middleware` no HTTP, `context manager` em jobs e `composition root` em fluxos realtime.
- Alteracoes de schema devem refletir com consistencia em `models`, `mappers` e `repositories`.

### Quando evitar

- Nao usar `repository` para encapsular regra de negocio ou `branching` funcional.
- Nao pular `mapper` para retornar `ORM` direto na borda por conveniencia.
- Nao abrir e fechar `session` em metodos pequenos quando o escopo transacional ja existe fora da camada.

## Regras de Integracao com Outras Camadas

### Mapa de integracao

| Camada | Relacao com `database` | Regra |
|---|---|---|
| `core` | Publica `interfaces`, `DTOs` e tipos de dominio | `database` implementa; `core` nunca importa de volta. |
| `rest` | Consome `repositories` via `pipes` | Nao deve acessar `ORM` diretamente. |
| `pubsub` | Pode instanciar `repositories` concretos em jobs | Deve controlar seu proprio escopo transacional. |
| `websocket` | Pode montar `repositories` concretos no `router` | Deve manter `ORM` longe dos `channels`. |

### Dependencias permitidas e proibidas

- `database` pode importar `entities`, `DTOs`, `structures` e `interfaces` do `core`.
- `database` nao deve depender de `rest/controllers`, `routers` HTTP ou `channels` para funcionar.

### Contratos de comunicacao

- `Repositories` concretos devem honrar exatamente as assinaturas e expectativas do `core`.
- Camadas externas devem receber tipos de dominio ou `DTOs`, nunca `Model` ORM como contrato publico.
- `Session` e transacao sao detalhes operacionais da camada, nao parte do dominio.

## Checklist Rapido para Novas Features na Camada

- [ ] Existe `model` ORM adequado para a persistencia envolvida.
- [ ] Existe `mapper` claro para traduzir entre banco e tipos do `core`.
- [ ] O `repository` implementa uma `interface` existente do `core` ou a porta foi criada antes no dominio.
- [ ] O ciclo de `Session` esta fora do `repository`.
- [ ] A mudanca considera evolucao de schema e sincronismo com o restante da camada.
- [ ] Nenhum `controller` ou `channel` passa a depender de `Model` ORM como contrato de saida.

## ✅ O que DEVE conter

- `Models`, `mappers` e `repositories` organizados por contexto e responsabilidade.
- Implementacoes concretas aderentes aos contratos do `core`.
- Infraestrutura de `Session` e `engine` centralizada.
- Nomes consistentes como `*Model`, `*Mapper` e `Sqlalchemy*Repository`.
- Conversao entre banco e dominio concentrada em poucos pontos previsiveis.

## ❌ O que NUNCA deve conter

- Regra de negocio, validacao de dominio ou decisao de fluxo HTTP.
- Dependencia de `APIRouter`, `Request`, `WebSocket`, `Depends(...)` ou `status code`.
- Exposicao de `ORM` como contrato publico da API.
- `commit()` e `rollback()` espalhados em `repositories` sem que a camada seja dona do escopo transacional.
