# Instruções para revisão com GitHub Copilot

## Antes de iniciar

* Leia o arquivo `AGENTS.md` antes de começar a revisão.
* Se houver uma issue vinculada ao pull request, leia a issue antes de analisar as alterações.

## O que deve ser validado

Ao revisar as alterações, identifique e reporte:

* problemas de **performance**
* problemas de **segurança**
* problemas de **concorrência**
* problemas de **acoplamento**
* problemas de **manutenibilidade**
* **duplicações** de código ou de lógica
* **ausência de testes** ou cobertura insuficiente
* problemas de **legibilidade**
* **erros de digitação**, nomes incorretos ou inconsistências de escrita

## Conformidade com padrões do projeto

Verifique se as alterações seguem os padrões definidos nos arquivos:

* `documentation/rules/code-conventions-rules.md`
* `documentation/rules/rules.md`

Além da convenção de código, confirme também que a implementação está adequada à **camada** e à **responsabilidade** do código alterado, respeitando os padrões arquiteturais e organizacionais descritos na documentação.

## Validação contra a issue

Se houver uma issue vinculada, use-a como referência para validar se a implementação:

* atende ao que foi solicitado
* respeita o escopo definido
* cobre os requisitos principais
* não introduz comportamento divergente do esperado

## Como reportar os problemas encontrados

Ao apontar problemas:

* seja **objetivo e específico**
* descreva **qual é o problema**
* explique **o impacto**
* sugira, sempre que possível, **uma ação corretiva**
* diferencie **problemas obrigatórios** de **sugestões de melhoria**

## Diretriz final

Priorize comentários relevantes, acionáveis e fundamentados nas regras do projeto, evitando observações genéricas ou subjetivas sem justificativa.
