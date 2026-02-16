# Regras da camada Routers

## Visao geral

A camada `src/equiny/routers/` e responsavel por compor a API HTTP no nivel de modulos.

Em outras palavras: **Router = composicao**, **Controller = endpoint**.

## Estrutura atual

```text
src/equiny/routers/
  auth/
    auth_router.py
  docs/
    docs_router.py
  profiling/
    profiling_router.py
    horses_router.py
```

## Padrao de implementacao

### Router Class Pattern

Routers sao definidos como classes com um metodo estatico `register() -> APIRouter`.
Exemplo (padrao usado no projeto):

```python
from fastapi import APIRouter
from equiny.rest.controllers.profiling import CreateHorseController


class HorsesRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/horses')

        CreateHorseController.handle(router)

        return router
```

### Inclusao de sub-routers

Um router de modulo pode incluir routers internos via `router.include_router(...)`.
No projeto, `ProfilingRouter` inclui `HorsesRouter`.

Regra pratica:

- **Router de modulo**: define `prefix` e `tags`.
- **Sub-router**: define apenas `prefix` (tags geralmente herdadas do modulo).

### Exportacao via `__init__.py`

Cada pacote expõe seus routers via `__init__.py` (com `__all__`) para permitir imports estaveis:

- `from equiny.routers.auth import AuthRouter`
- `from equiny.routers.profiling import ProfilingRouter`

## Integracao com a aplicacao

O registro global acontece no composition root do FastAPI:

- `src/equiny/app.py`: `FastAPIApp.register()` cria a app, registra middlewares e faz `app.include_router(<Router>.register())`.

Observacao importante (estado atual do projeto):

- A aplicacao desabilita `docs_url` e `redoc_url` no FastAPI.
- O router `DocsRouter` usa `include_in_schema=False` (a pagina existe, mas nao aparece no OpenAPI).

## Principios fundamentais

### ✅ O que DEVE conter

- **Agrupamento por contexto**: um router por modulo (ex: `AuthRouter`, `ProfilingRouter`).
- **Prefixos e tags**: definicao consistente de `prefix='/<modulo>'` e `tags=['<Nome> module']` quando aplicavel.
- **Composicao**: chamada de `Controller.handle(router)` para registrar endpoints.
- **Hierarquia**: uso de `include_router` para modularizar sub-recursos (`/profiling` -> `/horses`).

### ❌ O que NUNCA deve conter

- **Logica de endpoint**: nao declarar funcoes `@router.get/post/...` diretamente no router.
- **Regras de negocio**: nada de Core/UseCases/DTOs aqui.
- **Dependencias de request**: nao injetar repositorios/sessoes/usuario no router; isso e responsabilidade do controller (e seus Pipes/Depends).
- **Acesso a banco/ORM**: router nao conversa com SQLAlchemy.

## Convencoes de nomenclatura

- Diretorio por contexto: `routers/<context>/`.
- Arquivo: `<context>_router.py` ou `<resource>_router.py` (ex: `profiling_router.py`, `horses_router.py`).
- Classe: `PascalCase` + sufixo `Router` (ex: `ProfilingRouter`).
- Metodo: `register()` retorna `APIRouter`.

## Checklist rapido para adicionar um novo router

1. Criar pasta `src/equiny/routers/<context>/` com `__init__.py` exportando o router.
2. Criar `<context>_router.py` com `class <Context>Router` e `register() -> APIRouter`.
3. Definir `prefix` e (quando for modulo) `tags`.
4. Registrar controllers via `Controller.handle(router)`.
5. Se houver sub-recursos, criar sub-router e incluir via `router.include_router(SubRouter.register())`.
6. Registrar no app em `src/equiny/app.py` com `app.include_router(<Context>Router.register())`.
