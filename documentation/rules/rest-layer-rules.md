# Rest Layer Rules

## Visao geral e modulos da camada

A camada `src/equiny/rest/` e a borda HTTP da aplicacao.
Ela adapta request/response para os casos de uso da camada `core`.

Modulos atuais:

- `controllers/auth`: endpoints de autenticacao.
- `controllers/profiling`: endpoints de perfil de cavalo.
- `controllers/docs`: endpoint de renderizacao da pagina de documentacao.

Responsabilidade principal:

- receber entrada HTTP;
- validar/parsing da entrada;
- montar dependencias de borda (repositorio, sessao, etc.);
- chamar use case;
- devolver resposta tipada.

## Estrutura de diretorios explicada

Leitura por responsabilidade:

- `controllers/<modulo>`: classe por endpoint/caso de interacao.
- `__init__.py`: reexporta controllers publicos via `__all__`.
- composicao de prefixos/tags de rotas fica em `src/equiny/routers/`, fora dos controllers.

## Tooling da Camada REST

### Execução Local
- **Ferramenta:** `uv`
- **Comando:** `uv run dev`
- **Descrição:** Inicia a API em modo de desenvolvimento com hot-reload habilitado (via `uvicorn`).
- **Configuração:** O script `dev` está definido em `[project.scripts]` no `pyproject.toml` e aponta para `main:main`.

## Principios Fundamentais

### O que DEVE conter

- Controllers finos, sem regra de negocio.
- Metodo padrao `handle(router: APIRouter) -> None` para registrar rota.
- `status_code` explicito e coerente com o verbo HTTP.
- `response_model` explicito para rotas JSON.
- Entrada validada por schema (`BaseModel`) ou schema compartilhado.
- Delegacao de regra para use cases da camada `core`.

### O que NUNCA deve conter

- Regras de dominio dentro do endpoint.
- Query SQL direta ou manipulacao de modelo ORM como regra de API.
- Retorno de entidade de dominio ou modelo de banco como contrato HTTP.
- Commit/rollback manual de transacao no controller.
- Acoplamento a detalhes de roteamento global (prefixos, tags, app setup).
- Captura generica de excecao sem mapear corretamente para HTTP.

## Glossario arquitetural da camada REST

### Controller

Classe de adaptacao HTTP que registra rotas e traduz entrada/saida.
No projeto, segue padrao `ClassNameController.handle(router)`.

### Router

Componente de composicao de rotas (`APIRouter`) que define prefixos/tags,
inclui sub-rotas e chama `handle(...)` dos controllers.

### Schema de entrada

Modelo Pydantic usado para validar payload de request.
Exemplo: `HorseSchema` valida limites e converte para `HorseDto` via `to_dto()`.

### DTO de saida

Contrato serializavel retornado ao cliente.
No projeto, response usa DTOs da camada `core` (`HorseDto`, `AccountDto`).

### Use Case

Regra de aplicacao executada apos a adaptacao HTTP.
Controller instancia/injeta dependencias e chama `use_case.execute(...)`.

### Dependencia de request

Valor injetado por `Depends(...)` para integrar infraestrutura por request.
Exemplo atual: `Session` vindo de `Sqlalchemy.get_request_session`.

## Padroes de projeto e Padroes de uso aplicados

Padroes arquiteturais observados:

- Adapter pattern: controller como adaptador de HTTP para `core`.
- Thin Controller: endpoint delega quase toda logica ao use case.
- Dependency Injection (FastAPI Depends): injecao de `Session` por request.
- Ports and Adapters: REST usa interface/use case do `core`, nao implementacao interna.
- DTO boundary contract: serializacao via DTO, isolando dominio de detalhes HTTP.

Padrao de fluxo atual:

1. Router registra endpoint e chama controller.
2. Controller valida payload/path/query via tipagem/schema.
3. Controller monta repositorio concreto e use case.
4. Use case executa regra e retorna DTO.
5. FastAPI serializa resposta conforme `response_model`.

Mapeamento atual de endpoints:

- `POST /auth/sign-in` -> `SignInAccountController` -> `AccountDto`.
- `POST /profiling/horses` -> `CreateHorseController` -> `HorseDto`.
- `GET /profiling/horses/{horse_id}` -> `FetchHorseController` -> `HorseDto`.
- `GET /docs/` -> `RenderDocsPageController` -> `HTMLResponse`.

## Convencoes de nomenclatura

Convencoes observadas e recomendadas:

- Arquivos de controller em `snake_case` com sufixo `_controller.py`.
- Classes de controller em `PascalCase` com sufixo `Controller`.
- Metodo publico padrao `handle` estatico.
- Handler interno de rota pode usar nome `_` para escopo local.
- Imports em ordem: standard library, terceiros, projeto.
- Reexport de API publica em `__init__.py` com `__all__`.

## Regras de integracao com outras camadas da aplicacao

### Integracao com Core (`src/equiny/core/`)

- Controller so chama use cases e DTOs de `core`.
- Nenhuma regra de negocio deve ficar no controller.
- Erros de dominio devem ser convertidos para resposta HTTP na borda.

### Integracao com Validation (`src/equiny/validation/`)

- Sempre preferir schema dedicado para payload de entrada.
- Conversao schema -> DTO deve ocorrer antes da chamada do use case.
- Validacao de formato/limites fica em schema; regra de negocio permanece no `core`.

### Integracao com Database (`src/equiny/database/`)

- Controllers podem instanciar repositorio concreto da infra para injetar no use case.
- Sessao deve vir por `Depends(Sqlalchemy.get_request_session)`.
- Controller nao deve abrir/fechar/commitar transacao manualmente.

### Integracao com Routers (`src/equiny/routers/`)

- Prefixo, tags e composicao de rotas sao responsabilidade dos routers.
- Controller recebe `APIRouter` pronto e apenas registra endpoint.
- Rotas especiais (ex.: docs) podem configurar flags de schema no router, nao no controller.

### Integracao com Middlewares (`src/equiny/middlewares/`)

- Ciclo de vida da sessao e transacao e responsabilidade do middleware.
- Controller assume sessao disponivel no request e apenas consome a dependencia.

## Regras de testes da camada REST

### Objetivo dos testes REST

- Validar o contrato HTTP da borda: status code, payload e validacao de entrada.
- Garantir que regras de schema e serializacao estao corretas no endpoint.
- Cobrir comportamento observavel do cliente, nao detalhes internos de implementacao.

### Localizacao e nomenclatura

- Tests devem ficar em `tests/rest/controllers/<modulo>/`.
- Nome de arquivo: `test_<controller_name>.py`.
- Classe de teste: `Test<ControllerName>`.
- Nome de teste orientado a comportamento: `test_should_<resultado>_when_<condicao>`.

Exemplo atual:

- `tests/rest/controllers/profiling/test_create_horse_controller.py`

### Estrutura do teste

- Use `fastapi.testclient.TestClient` para exercitar a rota real.
- Organize cenarios em Arrange / Act / Assert.
- Em sucesso, valide `status_code` e campos principais do JSON.
- Em erro de validacao, valide ao menos `status_code == 422`.
- Use `pytest.mark.parametrize` para variacoes de entrada invalida quando aplicavel.

Padrao observado:

1. `client.post(...)` com payload.
2. Assert de `response.status_code`.
3. Assert de `response.json()` quando necessario.

### Escopo de mock e isolamento

- Para testes de contrato de endpoint, prefira nao mockar controller/use case e testar fluxo real da borda.
- Mocking e recomendado apenas quando o teste precisar isolar dependencia externa instavel (servico terceiro, fila, etc.).
- Nao mockar validacao de schema, pois ela faz parte do contrato REST.

No estado atual do projeto, os testes REST usam banco PostgreSQL de teste com schema isolado por sessao.

### Banco de dados em testes REST

- Reuse o fixture de `tests/conftest.py` para criar schema temporario e isolar execucao.
- Nao compartilhe estado entre testes; cada teste deve ser independente.
- Mantenha limpeza automatica no teardown (drop de tabelas/schema).

### Quando usar fakers

- Para payloads simples e pequenos, valores literais explicitos melhoram leitura.
- Use fakers quando houver muitos campos, cenarios combinatorios ou necessidade de dados variados.
- Se usar aleatoriedade, garanta previsibilidade (seed fixa) para evitar flaky tests.

### Boas praticas para testes REST

- Cubra caminho feliz e validacoes principais por endpoint.
- Prefira asserts objetivos sobre campos-chave em vez de snapshot grande de resposta.
- Teste uma regra por caso, com nome claro e intencao unica.
- Evite acoplar teste a mensagem textual exata de erro do framework.
- Mantenha testes rapidos e deterministas; evite dependencia de horario/ambiente sem controle.
- Sempre que adicionar endpoint novo, adicione ao menos um teste 2xx e um 4xx.

Checklist rapido para novos endpoints REST:

1. Criar controller em `src/equiny/rest/controllers/<modulo>/`.
2. Implementar `handle(router)` com rota, status e `response_model`.
3. Validar entrada com schema e delegar para use case do `core`.
4. Registrar controller no router da feature.
5. Cobrir fluxo feliz e falhas com testes de controller.

Checklist rapido para novos testes REST:

1. Criar arquivo em `tests/rest/controllers/<modulo>/test_<controller>.py`.
2. Usar fixture `client: TestClient`.
3. Cobrir um cenario de sucesso (2xx) com assert de payload.
4. Cobrir validacao principal (4xx, geralmente 422) para entrada invalida.
5. Reutilizar parametrizacao para variacoes de input invalido.
6. Garantir independencia entre testes (sem estado residual).
