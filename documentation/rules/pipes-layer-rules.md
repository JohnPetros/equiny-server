# Regras da camada Pipes

## Visao geral

A camada `src/equiny/pipes/` concentra provedores de dependencias para o FastAPI.
Ela padroniza a injecao via `fastapi.Depends`, mantem controllers magros, e centraliza
a criacao de adapters concretos (repositorios, providers, broker).

Pipes neste projeto nao sao "pipeline" de processamento. Sao dependency providers.

## Estrutura atual

```text
src/equiny/pipes/
  auth_pipe.py
  database_pipe.py
  providers_pipe.py
  pubsub_pipe.py
  storage_pipe.py
  __init__.py
```

Responsabilidade por modulo:

- `providers_pipe.py`: instancia providers (hash/jwt) sem depender de request.
- `database_pipe.py`: entrega repositorios SQLAlchemy usando a sessao da request.
- `pubsub_pipe.py`: entrega `Broker` usando o client Inngest da request.
- `auth_pipe.py`: dependencies reutilizaveis de autenticacao (guards).
- `storage_pipe.py`: valida e transforma arquivos de entrada (`UploadFile`) em DTOs do dominio (`FileDto`).

## Principios fundamentais

### ✅ O que DEVE conter

- Funcoes pequenas e deterministicas: cada Pipe faz uma coisa (obter/criar dependencia).
- Integracao com FastAPI: assinaturas pensadas para uso com `Depends(...)`.
- Retorno por interface: quando existir interface no Core, retorne a interface (ex: `HorsesRepository`, `Broker`).
- Criacao de adapters concretos: encapsular `Sqlalchemy*Repository`, `InngestBroker`, etc.
- Uso de `request.state` para contexto de request: obter recursos criados por middlewares (sessao, clients).

### ❌ O que NUNCA deve conter

- Regras de negocio: Pipe nao chama UseCase e nao decide comportamento de dominio.
- Logica HTTP: nao montar Response, nao definir status code, nao acessar `APIRouter`.
- Transacoes: nao fazer commit/rollback (isso e do middleware de sessao).
- Estado global de request: nao guardar session/client em variaveis globais.
- Dependencias opacas: se algo vem de `request.state`, garanta middleware registrado e documente.

## Padroes aplicados no projeto

### ProvidersPipe

`ProvidersPipe` concentra providers sem estado e sem request:

- `ProvidersPipe.get_hash_provider() -> HashProvider`
- `ProvidersPipe.get_jwt_provider() -> JoseJwtProvider`
- `ProvidersPipe.get_cache_provider() -> CacheProvider`

Regra: providers simples podem ser instanciados aqui. Prefira tipar o retorno por interface quando possivel.

### DatabasePipe (Session por request)

`DatabasePipe` depende da sessao SQLAlchemy salva em `request.state.sqlalchemy_session`.
Esse valor e definido pelo middleware `HandleSqlalchemySessionMiddleware`.

Padrao atual:

- `get_sqlalchemy_session(request: Request) -> Session`
- `DatabasePipe.get_*_repository(sqlalchemy: Annotated[Session, Depends(get_sqlalchemy_session)]) -> <RepoInterface>`

Regra: controllers devem depender do repositorio via `Depends(DatabasePipe.get_*_repository)`
e nao criar repositorio manualmente.

### PubSubPipe (Client por request)

`PubSubPipe` depende do client Inngest salvo em `request.state.inngest_client`.
Esse valor e definido pelo middleware `HandleInngestClientMiddleware`.

Padrao atual:

- `get_inngest_client(request: Request)` retorna o client salvo no state
- `PubSubPipe.get_broker(inngest: Inngest = Depends(get_inngest_client)) -> Broker`

Regra: expor para o controller a interface do Core (`Broker`), nao o SDK.

### StoragePipe (Validacao de entrada)

`StoragePipe` centraliza validacao e transformacao de arquivos de upload:

- `StoragePipe.get_image_files(files: list[UploadFile]) -> list[FileDto]`

Comportamento:

- Valida se todos os arquivos possuem `Content-Type` iniciando com `image/`.
- Retorna HTTP 415 (UNSUPPORTED_MEDIA_TYPE) imediatamente para arquivos invalidos.
- Converte `UploadFile` (FastAPI) para `FileDto` (dominio) preservando nome, dados e content-type.

Padrao de uso no controller:

```python
from fastapi import Depends
from equiny.pipes.storage_pipe import StoragePipe

@router.post('/images/upload')
def _(
    files_dto: list[FileDto] = Depends(StoragePipe.get_image_files),
):
    ...
```

Regra: pipes de validacao de entrada devem falhar rapido (fail-fast) na borda REST,
retornando codigos HTTP apropriados antes de chegar ao controller ou use case.

### AuthPipe (guards)

`AuthPipe` expoe dependencies reutilizaveis para proteger endpoints.
No estado atual existe:

- `AuthPipe.verify_jwt(request: Request, jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider)) -> None`

Comportamento atual:

- Le o header `Authorization`.
- Se nao existir, levanta `AuthError`.
- Se existir, delega para `jwt_provider.decode(token)`.

Padrao de uso no controller:

```python
from fastapi import Depends
from equiny.pipes.auth_pipe import AuthPipe

@router.post(
    '/',
    dependencies=[Depends(AuthPipe.verify_jwt)],
)
def _( ... ):
    ...
```

Regra: AuthPipe pode validar credenciais e levantar erro de autenticacao, mas nao deve
acessar repositorios nem carregar conta/usuario (isso vira um Pipe dedicado quando existir).

## Exportacao do pacote

`src/equiny/pipes/__init__.py` exporta `DatabasePipe`, `PubSubPipe`, `ProvidersPipe` e `StoragePipe` via `__all__`.
`AuthPipe` e importado diretamente do modulo `equiny.pipes.auth_pipe`.

## Integracao com outras camadas

- `src/equiny/rest/controllers/`: consome Pipes via `Depends(...)`.
- `src/equiny/rest/middlewares/`: popula `request.state` (sessao SQLAlchemy e client Inngest).
- `src/equiny/app.py`: registra middlewares e compoe routers; isso garante que `request.state` exista para Pipes.

## Checklist rapido para criar um novo Pipe

1. Criar `src/equiny/pipes/<assunto>_pipe.py`.
2. Definir funcao(s) e/ou `class <Assunto>Pipe` com metodos `@staticmethod`.
3. Retornar interfaces do Core sempre que possivel.
4. Se depender de `request.state`, garantir middleware registrado em `src/equiny/app.py`.
5. Consumir no controller via `Depends(<Pipe>.<metodo>)`.
6. Exportar no `src/equiny/pipes/__init__.py` se for Pipe de uso amplo.
