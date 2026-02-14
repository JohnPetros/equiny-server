---
description: Concluir spec com validacao de qualidade, requisitos e documentacao
---

# Prompt: Concluir spec (equiny-server)

Objetivo: finalizar e consolidar a implementacao de uma spec tecnica no
`equiny-server`, garantindo codigo polido, validado e pronto para PR.

Entrada:

- Spec tecnica que guiou a implementacao.
- Codigo implementado (mudancas em `core`, `database`, `rest`, `validation`, etc.).

Diretrizes de execucao:

1. Validacao final de qualidade (comandos do repo)

- Lint/format: `uv run poe codecheck`
- Typecheck: `uv run poe typecheck`
- Testes: `uv run poe test`

2. Verificacao de requisitos

- Compare o codigo final com os requisitos/criterios de aceite da spec.
- Garanta que limites arquiteturais foram respeitados:
  - `core` puro (sem FastAPI/SQLAlchemy/HTTP/env)
  - `database` apenas persistencia/mapeamento
  - `rest` valida/adapta/delega (controller fino)

3. Atualizacao de documentacao

- Se a implementacao mudou decisoes da spec, atualize a propria spec com o que foi decidido.
- Se houver mudanca arquitetural relevante (nova camada/padrao/fluxo), atualize `documentation/architecture.md`.
- Se a mudanca introduz regras novas/ajustes de padrao, atualize `documentation/rules/*.md`.

4. Status da spec

- Marque a spec como concluida e atualize a data de ultima atualizacao (se o documento usar esse campo).

5. Resumo final para PR

- Liste o que foi entregue (por camada/modulo).
- Destaque mudancas de contrato (HTTP/DTOs), migracoes e riscos.
- Inclua comandos rodados e o resultado (passando).
