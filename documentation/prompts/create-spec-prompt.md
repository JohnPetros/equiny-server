---
description: Criar spec tecnica detalhada para implementacao no equiny-server
---

# Prompt: Criar Spec (equiny-server)

**Objetivo:** detalhar a implementacao tecnica de uma `feature`, `fix` ou `refactor` no `equiny-server`, atuando como um Tech Lead Senior. A `spec` deve ser uma ponte entre contexto de produto e implementacao, com nivel de detalhe suficiente para executar o trabalho sem ambiguidades.

**Contexto do projeto (leitura minima obrigatoria):**

- Produto (alto nivel): PRD do Equiny (MVP) em `documentation/overview.md` (fonte externa)
- Arquitetura: `documentation/architecture.md`
- Regras por camada: `documentation/rules/rules.md` (e os docs acionados por ele)

## Entrada

- Enunciado da mudanca (1-3 paragrafos) e motivacao.
- Links para PRD/issue/discussao (se existirem).
- Acesso a codebase atual para validacao de caminhos e exemplos similares.

## Diretrizes de execucao

1. **Pesquisa e contextualizacao (sem expor `chain-of-thought`):**
   - leia o PRD referente a spec.
   - Identifique **objetivo**, **escopo** e **risco**.
   - Mapeie o fluxo principal: `HTTP` -> `Router` -> `Controller` -> `Pipe/Depends` -> `UseCase` -> `Repository` -> `SQLAlchemy` -> `PostgreSQL`.
   - Leia e aplique as regras relevantes que envolvam a spec em `documentation/rules/rules.md`:
   - Reuse/extenda componentes existentes; evite duplicidade de `UseCase`, `DTO`, `Pipe`, `Mapper` e `Repository`.
   - Use sua tool de `question` para me fazer perguntas sobre a implementação ou incongruencias encontradas.

2. **Ferramentas auxiliares:**
   - Use Serena para localizar arquivos e exemplos na codebase.
   - Use Context7 apenas quando precisar de documentacao/exemplos de uma biblioteca especifica.

3. **Qualidade e densidade:**
   - Seja direto; prefira listas e tabelas a blocos longos.
   - Use **negrito** para conceitos/decisoes e `code` para termos tecnicos (ex: `FastAPI`, `Depends`, `Session`, `DTO`, `UseCase`).
   - Escreva em PT-BR; mantenha termos de programacao em Ingles e em `code`.

## Estrutura do documento (modelo obrigatorio)

Use frontmatter e a hierarquia de cabecalhos sem pular niveis.

```md
---
title: <Titulo claro>
prd: <link para o PRD referente a spec, que esta no nivel acima do diretório da spec>
status: <em progresso|concluido>
last_updated_at: <data da ultima atualizacao>
---

# 1. Objetivo
<1 paragrafo: o que sera entregue funcionalmente e tecnicamente.>

# 2. Escopo

## 2.1 In-scope
- ...

## 2.2 Out-of-scope
- ...

# 3. Requisitos

## 3.1 Funcionais
- ...

## 3.2 Nao funcionais
- ...

# 4. Regras de negocio e invariantes
- ...

# 5. O que ja existe (inventario)

> ⚠️ Inclua apenas itens realmente relevantes para implementar a mudanca.

## 5.1 Core (`src/equiny/core/`)
- **`NomeDaClasse`** (`src/equiny/...`) - <por que existe e como sera reutilizada>

## 5.2 Database (`src/equiny/database/`)
- **`NomeDaClasse`** (`src/equiny/...`) - ...

## 5.3 REST/Controllers (`src/equiny/rest/`)
- **`NomeDaClasse`** (`src/equiny/...`) - ...

## 5.4 Routers (`src/equiny/routers/`)
- **`NomeDaClasse`** (`src/equiny/...`) - ...

## 5.5 Validation (`src/equiny/validation/`)
- **`NomeDaClasse`** (`src/equiny/...`) - ...

## 5.6 Pipes e Middlewares
- **`NomeDaClasse`** (`src/equiny/pipes/...`) - ...
- **`NomeDaClasse`** (`src/equiny/rest/middlewares/...`) - ...

# 6. O que deve ser criado

> 🛠️ Liste arquivos novos por camada. Para cada arquivo, detalhe **assinatura**, **responsabilidade** e **dependencias**.
> Caso alguma seção não esteja envolvida na implementação, ignore-a na spec.

## 6.1 Core

## 6.1.1 Domain (Entities/Structures/Errors/Events)
- **Arquivo:** `src/equiny/core/<context>/domain/...`
  - **Tipo:** `entity` | `structure` | `error` | `event`
  - **Responsabilidade:** ...
  - **Assinatura/contratos:** ...
  - **Dependencias:** ...
  - **Observacoes:** ...

## 6.1.2 Interfaces
- **Arquivo:** `src/equiny/core/<context>/interfaces/...`
  - **Interface:** `...Repository`
  - **Metodos:** `...`
  - **Semantica:** ...

## 6.1.3 Use Cases
- **Arquivo:** `src/equiny/core/<context>/use_cases/...`
  - **Use case:** `*UseCase`
  - **Entrada:** `*Dto`
  - **Saida:** `*Dto`
  - **Dependencias:** `*Repository`, ...
  - **Fluxo:** (passo a passo, curto)

## 6.2 Validation
- **Arquivo:** `src/equiny/validation/...`
  - **Schema:** `*Schema`
  - **Campos:** ...
  - **`to_dto()`**: `-> <Dto>`

## 6.3 Database

## 6.3.1 Models
- **Arquivo:** `src/equiny/database/sqlalchemy/models/...`
  - **Model:** `*Model`
  - **Tabela:** `<table>`
  - **Campos/indices:** ...

## 6.3.2 Mappers
- **Arquivo:** `src/equiny/database/sqlalchemy/mappers/...`
  - **Mapper:** `*Mapper`
  - **Conversao:** `Model <-> Entity/Dto`

## 6.3.3 Repositories
- **Arquivo:** `src/equiny/database/sqlalchemy/repositories/...`
  - **Repository:** `Sqlalchemy*Repository`
  - **Implementa:** `*Repository`
  - **Metodos:** ...

## 6.3.4 Migracoes (Alembic)
- **Mudanca de schema:** <descrever>
- **Nova migration:** `alembic/versions/<...>.py`

## 6.4 Pipes
- **Arquivo:** `src/equiny/pipes/..._pipe.py`
  - **Pipe:** `*Pipe`
  - **Fornece:** `Repository` | `Provider` | `Broker`
  - **Origem:** `request.state` | singleton

## 6.5 REST 

### 6.5.1 Controllers
- **Arquivo:** `src/equiny/rest/controllers/...`
  - **Controller:** `*Controller`
  - **Rota (relativa):** `/<path>`
  - **`status_code`:** `HTTPStatus...`
  - **`response_model`:** `<Dto>`
  - **Dependencias:** `Depends(*Pipe.*)`

## 6.6 Routers
- **Arquivo:** `src/equiny/routers/...`
  - **Router:** `*Router`
  - **Prefixo:** `/<prefix>`
  - **Controllers:** `*Controller.handle(...)`

# 7. O que deve ser modificado

> ⚠️ Liste apenas arquivos existentes. Mudancas em arquivos novos devem ficar na secao 6.

- **Arquivo:** `src/equiny/...`
  - **Mudanca:** ...
  - **Justificativa:** ...
  - **Camada:** `core` | `database` | `rest` | `routers` | `validation` | `pipes/middlewares`

# 8. O que deve ser removido

> ⚠️ Remocoes precisam ser justificadas e seguras (sem quebrar imports/public API). Se houver substituicao, aponte o novo caminho.

- **Arquivo:** `src/equiny/...`
  - **Remocao:** ...
  - **Motivo:** ...
  - **Substituir por (se aplicavel):** `src/equiny/...`

# 9. Fluxo e diagramas

## 9.1 Fluxo de dados (ASCII)
```text
Client -> Router -> Controller -> Pipe/Depends -> UseCase -> Repository -> DB
```

## 9.2 Referencias internas
- `src/equiny/...` (exemplo similar)
```

**Regras**

- Nao inclua testes automatizados na `spec`.
- Todos os caminhos citados devem existir no projeto (ou estar explicitamente marcados como **novo arquivo**).
