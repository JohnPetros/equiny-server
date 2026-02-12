# Regras de leitura progressiva (Progressive Disclosure)

Objetivo: reduzir contexto desnecessario e ler apenas as regras certas para cada
tipo de tarefa. Use este documento como porta de entrada antes de consultar os
demais arquivos em `documentation/rules/`.

## Ordem recomendada de leitura

- Comece por este arquivo (`rules.md`).
- Leia apenas os documentos acionados pelo tipo de mudanca.
- Se a tarefa crescer de escopo, desbloqueie o proximo documento necessario.
- Em caso de duvida entre duas camadas, leia primeiro regra geral da camada e
  depois regra especifica de teste.

## `documentation/rules/code-conventions-rules.md`

Quando ler:

- SEMPRE que realizar qualquer alteracao ou escrita de codigo.
- Antes de executar tarefas de validacao (`uv run poe codecheck` ou `uv run poe typecheck`).
- Ao padronizar estilo de codigo em features novas ou refactors.
- Ao revisar consistencia de nomenclatura e organizacao de arquivos.
- Ao preparar PR com mudancas amplas para evitar divergencia de estilo.

Instrucoes praticas:

- Siga convencoes de nomes do projeto (arquivos, classes, sufixos de papel).
- Preserve estrutura de modulos e exports publicos (`__init__.py`/`__all__`).
- Priorize legibilidade e consistencia com o padrao ja existente.
- Evite introduzir padrao novo sem necessidade arquitetural clara.

## `documentation/rules/core-layer-rules.md`

Quando ler:

- Ao criar/alterar entidades, structures, DTOs, erros de dominio ou use cases.
- Ao revisar limites arquiteturais entre `core` e outras camadas.
- Ao validar dependencia correta entre `core`, `rest` e `database`.

Instrucoes praticas:

- Mantenha o `core` puro: sem FastAPI, ORM, SQL, sessao, env var ou HTTP.
- Centralize regra de negocio em entidades/structures/use cases.
- Use interfaces (ports) para dependencias externas.
- Garanta convencoes de nome: `*UseCase`, `*Dto`, `*Repository`, `execute(...)`.

## `documentation/rules/database-rules.md`

Quando ler:

- Ao criar/alterar models, mappers, repositorios SQLAlchemy ou sessao DB.
- Ao integrar persistencia nova com interfaces do `core`.
- Ao ajustar fluxo de transacao por request (middleware + Session).

Instrucoes praticas:

- Implemente apenas persistencia e mapeamento; sem regra de negocio.
- Respeite exatamente o contrato das interfaces definidas no `core`.
- Use mapper para traducao dominio <-> ORM; nao exponha ORM para bordas.
- Nao espalhe commit/rollback em repositorios; ciclo transacional fica no middleware.

## `documentation/rules/rest-layer-rules.md`

Quando ler:

- Ao criar/alterar controllers, rotas e contratos HTTP.
- Ao mexer em integracao com schema de validacao ou `response_model`.
- Ao conectar endpoint a use case e repositorio concreto.

Instrucoes praticas:

- Mantenha controller fino: valida/adapta/delega, sem regra de negocio.
- Defina `status_code` e `response_model` explicitos nos endpoints.
- Converta entrada para DTO antes de chamar use case.
- Use dependencia de `Session` por `Depends(...)` e sem controlar transacao no controller.

## `documentation/rules/testing-rules.md`

Quando ler:

- Ao criar/alterar testes e precisar decidir rapidamente qual padrao aplicar.
- Ao trabalhar em PR que mistura testes de `core` e `rest`.
- Ao revisar cobertura minima esperada por tipo de teste.

Instrucoes praticas:

- Use como indice de decisao para direcionar a estrategia de teste.
- Aplique nomenclatura e estrutura AAA de forma consistente.
- Garanta cenarios de sucesso e falha relevantes para cada unidade testada.
- Se envolver testes especificos de use case/controller, complemente com as regras especializadas correspondentes.

## Regra de acionamento rapido

- Mudou regra de negocio -> leia `core-layer-rules.md`.
- Mudou persistencia/SQLAlchemy -> leia `database-rules.md`.
- Mudou endpoint/contrato HTTP -> leia `rest-layer-rules.md`.
- Mudou testes -> leia `testing-rules.md` (e depois regras especializadas quando necessario).
- Mudou estilo/nomeacao/organizacao -> leia `code-conventions-rules.md`.
