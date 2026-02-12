# Regras gerais de leitura para testes

## Tooling de Testes

### Framework
- **Ferramenta:** `pytest`
- **Uso:** Framework padrão para execução e escrita de testes.
- **Comando:** `uv run poe test` (executa `pytest -v`).

### Configuração
- **Arquivo:** `pyproject.toml` (seção `[tool.pytest.ini_options]`).
- **Plugins:** `pytest-cov` (cobertura), `pytest-asyncio` (para testes assíncronos, se aplicável).

## Use Cases

- Leia `documentation/rules/use-cases-testing-rules.md` antes de criar, alterar ou revisar testes unitarios em `tests/core/**/use_cases/`.
- Leia `documentation/rules/use-cases-testing-rules.md` quando estiver testando regra de negocio da camada `core` (com mocks de ports/repositorios e foco em `use_case.execute`).

## Controllers

- Leia `documentation/rules/controllers-testing-rules.md` antes de criar, alterar ou revisar testes de controllers em `tests/rest/controllers/**`.
- Leia `documentation/rules/controllers-testing-rules.md` quando o objetivo for validar contrato HTTP (status code, payload, validacao de entrada e comportamento de endpoint).
- Se a tarefa envolver testes nas duas camadas (`core` e `rest`), leia primeiro `documentation/rules/use-cases-testing-rules.md` e depois `documentation/rules/controllers-testing-rules.md`.
- Em PRs que adicionam endpoints novos e/ou use cases novos, releia ambos os documentos antes de finalizar para garantir cobertura e padrao de nomenclatura.
