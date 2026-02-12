# Regras da camada REST

## Visao geral e modulos da camada

A camada `src/equiny/rest/` atua como o adaptador de entrada (Driver Adapter) da aplicacao.
Ela e responsavel por expor a interface HTTP, receber requisicoes, validar entradas,
converter dados e delegar a execucao para os Casos de Uso (Core).

Modulos atuais:

- `controllers`: Agrupamento de controladores por contexto (`auth`, `profiling`, etc.).
- `docs`: Controladores para documentacao ou paginas estaticas.
- `middlewares`: Logica transversal (cross-cutting concerns) como gestao de sessao de banco e integracao com clientes externos (Inngest).

Responsabilidade de alto nivel:

- Definir contratos de entrada (Schemas) e saida (Response Models).
- Gerenciar codigos de status HTTP (`201`, `400`, `404`, etc.).
- Orquestrar a obtencao de dependencias (via Pipes) e injecao em casos de uso.
- Traduzir excecoes de dominio para respostas HTTP adequadas.

## Estrutura de diretorios explicada

```text
src/equiny/rest/
  controllers/
    auth/
      sign_in_account_controller.py
      ...
    profiling/
      create_horse_controller.py
      ...
    docs/
      render_docs_page_controller.py
  middlewares/
    handle_sqlalchemy_session_middleware.py
    ...
```

Leitura por responsabilidade:

- `controllers/<context>/<action>_controller.py`: Implementacao de um endpoint especifico.
- `middlewares/handle_<responsibility>_middleware.py`: Implementacao de middlewares do FastAPI.

## Principios Fundamentais

### ✅ O que DEVE conter

- **Controllers "Magros"**: Apenas logica de adaptador (HTTP -> Dominio -> HTTP).
- **Validacao de Entrada**: Uso de Pydantic Schemas (`src/equiny/validation`) ou `Body` models locais.
- **Injecao de Dependencia**: Uso de `Depends` do FastAPI juntamente com classes `Pipe` (ex: `DatabasePipe`, `AuthPipe`) para obter repositorios e servicos.
- **Delegacao**: Instanciar Casos de Uso com as dependencias injetadas.
- **Retorno Tipado**: Uso explicito de `response_model` com DTOs do Core.
- **Status Codes**: Uso de `http.HTTPStatus` para clareza (ex: `HTTPStatus.CREATED`).

### ❌ O que NUNCA deve conter

- **Regras de Negocio**: Condicionais de logica de dominio, validacoes de negocio complexas.
- **Acesso Direto ao ORM**: Queries SQL ou manipulacao de modelos do SQLAlchemy diretamente no controller.
- **Instanciacao Manual de Repositorios**: Evite `Repo(session)`. Use `Depends(DatabasePipe.get_repo)` para manter o acoplamento baixo e facilitar testes.
- **Gestao de Transacao**: Commit/Rollback explicito (deixe para o Middleware `HandleSqlalchemySessionMiddleware`).
- **Retorno de Models ORM**: Nunca retornar um objeto `Model` do SQLAlchemy diretamente no `response_model`.

## Padroes de projeto e Padroes de uso aplicados

### Controller Class Pattern

Os controllers sao definidos como classes com um metodo estatico `handle`:

```python
class CreateHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(...)
        async def _(
            body: Schema,
            repository: InterfaceRepository = Depends(DatabasePipe.get_repository)
        ):
            ...
```

Isso permite agrupar dependencias e manter o escopo limpo. O metodo interno (geralmente `_`) e a funcao de rota real.

### Dependency Injection (Pipes)

A camada REST utiliza "Pipes" (`src/equiny/pipes/`) como provedores de dependencias para o FastAPI:

1.  **DatabasePipe**: Fornece repositorios concretos (`Sqlalchemy*Repository`) ja inicializados com a sessao da requisicao.
2.  **AuthPipe**: Fornece validacao de token e usuario autenticado.

O fluxo tipico em um controller e:

1.  Declarar dependencia do repositorio via `Depends(DatabasePipe.get_*)`.
2.  Instanciar o Caso de Uso passando o repositorio injetado.
3.  Executar `use_case.execute(dto)`.

### Input/Output Conversion

- **Input**: `Schema` (Validation) -> `to_dto()` -> `DTO` (Core).
- **Output**: `DTO` (Core) -> `Response Model` (FastAPI serializa automaticamente).

## Convencoes de nomenclatura

- Arquivos em `snake_case` refletindo a acao: `create_horse_controller.py`.
- Classes em `PascalCase` com sufixo `Controller`: `CreateHorseController`.
- Metodo de entrada padrao: `handle(router: APIRouter)`.
- Funcao de rota interna: `async def _(...)`.

## Regras de integracao com outras camadas da aplicacao

### Integracao com Core (`src/equiny/core/`)

- Controllers importam `UseCases`, `DTOs` e `Interfaces` de repositorios.
- Controllers nao implementam regras, apenas chamam `execute()`.

### Integracao com Database (`src/equiny/database/`)

- **Indireta via Pipes**: Controllers NAO devem importar `Sqlalchemy` ou classes concretas de repositorios diretamente.
- O `DatabasePipe` encapsula a criacao dos repositorios concretos.

### Integracao com Validation (`src/equiny/validation/`)

- Schemas sao usados como type hints nos argumentos da funcao de rota.
- O metodo `to_dto()` do schema deve ser usado para converter para o tipo esperado pelo Use Case.

### Integracao com Routers (`src/equiny/routers/`)

- Os arquivos de rotas (`src/equiny/routers/*.py`) definem classes com metodos estaticos `register() -> APIRouter`.
- O metodo `register` configura prefixos e tags.
- Controllers sao registrados chamando `Controller.handle(router)`.
- Routers podem incluir sub-routers via `router.include_router(...)`.
- O controller nao define o prefixo do modulo (ex: `/horses`), apenas o caminho relativo da acao (ex: `/` ou `/{id}`).

## Checklist rapido para novas features na camada `rest`

1.  Definir/Reutilizar Schema em `validation` (ou local se for muito simples).
2.  Criar arquivo do controller em `rest/controllers/<context>/`.
3.  Implementar classe `*Controller` e metodo `handle`.
4.  Definir rota, status code e `response_model` (DTO).
5.  Injetar dependencias (Repositorios/Servicos) via `Depends(DatabasePipe.*)`.
6.  Instanciar Use Case com as dependencias.
7.  Chamar `execute` e retornar resultado.
8.  Registrar controller no arquivo de rotas correspondente em `routers/`.
