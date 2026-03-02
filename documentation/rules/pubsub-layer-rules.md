# Regras da Camada PubSub

# Visao Geral
- Objetivo da camada
  - Executar processamento assincrono orientado a **eventos de dominio**, usando `Inngest` como broker e runtime de jobs.
  - Expor funcoes/jobs do `Inngest` via `FastAPI` (adapter de entrada) e publicar eventos do dominio via `Broker` (porta do `core`).
- Responsabilidades principais
  - Registrar e servir funcoes do `Inngest` no app: `src/equiny/pubsub/inngest/inngest_pubsub.py`.
  - Publicar eventos do dominio (adapter do `Broker`): `src/equiny/pubsub/inngest/inngest_broker.py`.
  - Implementar jobs assincronos que consomem eventos e orquestram `UseCase` do `core`: `src/equiny/pubsub/inngest/jobs/`.
  - Gerenciar ciclo de vida de `Session` SQLAlchemy em jobs (`commit`/`rollback`/`close`): `src/equiny/pubsub/inngest/jobs/job.py`.
- Limites da camada
  - A camada `pubsub` deve ser **orquestracao**: validar payload, abrir recursos (sessao), instanciar repositorio/use case e executar.
  - A camada `pubsub` nao deve conter **regra de negocio**; regra de negocio pertence ao `core`.
  - A camada `pubsub` nao deve expor o SDK do `Inngest` para o `core` (o `core` fala via `Broker`).

# Estrutura de Diretorios Globais
- Mapa de pastas relevantes
  - `src/equiny/pubsub/`
  - `src/equiny/pubsub/inngest/`
  - `src/equiny/pubsub/inngest/jobs/`
  - `src/equiny/pubsub/inngest/jobs/profiling/`
- Responsabilidade de cada diretorio
  - `src/equiny/pubsub/`: pacote da camada; exporta `InngestPubSub` via `__all__`.
  - `src/equiny/pubsub/inngest/`: integracao com `Inngest` (registro/serve e broker).
  - `src/equiny/pubsub/inngest/jobs/`: base de job e jobs por contexto.
  - `src/equiny/pubsub/inngest/jobs/<contexto>/`: jobs agrupados por **bounded context** (ex: `profiling`).
- Regras de organizacao e nomeacao
  - Jobs devem viver em `src/equiny/pubsub/inngest/jobs/<contexto>/`.
  - Um job deve ser uma classe `*Job` com metodos `@staticmethod`, seguindo o padrao usado em `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`.
  - A exportacao do pacote deve ser explicita via `__init__.py` + `__all__` (ex: `src/equiny/pubsub/inngest/jobs/profiling/__init__.py`).

> 💡 Regra pratica: se voce criou um job novo e ele nao esta registrado em `src/equiny/pubsub/inngest/inngest_pubsub.py`, ele nao sera executado.

# Principios Fundamentais
## Deve conter
- Elementos obrigatorios da camada
  - **Jobs magros**: receber evento -> validar payload -> executar 1 acao principal (orquestracao) -> delegar regra de negocio para `UseCase`.
  - **Validacao de payload** via Pydantic (`BaseModel.model_validate(...)`) dentro do job.
  - **Gestao de sessao** SQLAlchemy em jobs via `Job.sqlalchemy_session()`: `src/equiny/pubsub/inngest/jobs/job.py`.
  - **Publicacao de eventos** via porta `Broker`: `src/equiny/core/shared/interfaces/broker.py` + adapter `src/equiny/pubsub/inngest/inngest_broker.py`.
  - **Uso de step** do `Inngest` para a acao principal, seguindo o padrao atual em `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py` (`context.step.run(...)`).
- Praticas recomendadas
  - Jobs devem ser **idempotentes** (a mesma execucao pode acontecer mais de uma vez sem corromper estado).
  - Jobs devem manter o numero de efeitos colaterais no minimo e centralizar a mudanca de estado no `UseCase`.
  - Jobs devem tipar o payload com schemas reutilizados quando existirem (ex: `equiny.validation.shared`).

## Nao deve conter
- Antipadroes e acoplamentos proibidos
  - Job nao deve implementar validacoes e regras de negocio (isso e do `core`).
  - Job nao deve manipular **Models ORM** diretamente nem escrever queries: use repositorios SQLAlchemy existentes.
  - Job nao deve fazer `commit()`/`rollback()` manual fora do context manager; o ciclo transacional e do `Job.sqlalchemy_session()`.
  - Job nao deve depender de `controllers`/`routers`/`pipes`; `pubsub` e uma borda propria.
- Responsabilidades que pertencem a outras camadas
  - Contratos HTTP e status codes pertencem a `rest`/`routers`.
  - Definicao de eventos de dominio pertence a `core/*/domain/events/`.
  - Persistencia (models/mappers/repos) pertence a `src/equiny/database/sqlalchemy/`.

> ⚠️ Se voce esta prestes a "resolver" um problema de dominio dentro do job, isso e sinal de que a regra deveria estar em um `UseCase` no `core`.

# Padroes de Projeto
- Padroes arquiteturais aceitos
  - Ports and Adapters: `core` define a porta `Broker` (`src/equiny/core/shared/interfaces/broker.py`) e `pubsub` implementa o adaptador concreto (`src/equiny/pubsub/inngest/inngest_broker.py`).
  - Orquestracao por UseCase: job instancia repositorio + `UseCase` e chama `execute(...)`.
- Como aplicar cada padrao na camada
  - Registro do Inngest no app deve acontecer via `InngestPubSub.register(app)`: `src/equiny/pubsub/inngest/inngest_pubsub.py`.
  - Publicacao de evento deve receber um `Event` do dominio e enviar para o Inngest com `name` e `payload`: `src/equiny/pubsub/inngest/inngest_broker.py`.
  - Job deve:
    - Definir `PayloadSchema(BaseModel)`.
    - Criar handler via `@inngest.create_function(...)`.
    - Validar `context.event.data` com `PayloadSchema.model_validate(...)`.
    - Executar a acao principal via `context.step.run(...)`.
    - Abrir sessao DB com `Job.sqlalchemy_session()` e instanciar repositorio + use case.
- Quando evitar cada padrao
  - Nao criar job para logica que precisa ser sincrona/transactional com a request HTTP; isso pertence ao fluxo REST.
  - Nao publicar eventos diretamente do `database` ou do `core` com SDK do Inngest; sempre via `Broker` (porta) no `core`.

```python
# Exemplo real do projeto (estrutura do job):
# `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`

from pydantic import BaseModel
from inngest import Inngest, Context, TriggerEvent

from equiny.core.auth.domain.events import AccountCreatedEvent


class _PayloadSchema(BaseModel):
    ...


class CreateOwnerJob:
    @staticmethod
    def handle(inngest: Inngest):
        @inngest.create_function(
            fn_id='profiling/create.owner.job',
            trigger=TriggerEvent(event=AccountCreatedEvent.name),
        )
        async def _(context: Context) -> None:
            payload = _PayloadSchema.model_validate(context.event.data)
            await context.step.run('Create owner', lambda: CreateOwnerJob.create_owner(payload))

        return _
```

# Padroes de Uso Aplicados
- Fluxos comuns da camada
  - Publicacao: `core` cria `Event` -> borda (ex: REST) recebe `Broker` via `Depends` -> `InngestBroker.publish(event)`.
  - Consumo: Inngest dispara job -> job valida payload -> job abre sessao -> job executa `UseCase`.
- Exemplos de uso correto
  - Job de exemplo: `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py`.
    - Evento: `AccountCreatedEvent` (importado do `core`).
    - Payload tipado e validado com `PayloadSchema`.
    - Execucao de `CreateOwnerUseCase` usando `SqlalchemyOwnersRepository` dentro de `Job.sqlalchemy_session()`.
- Erros comuns e como evitar
  - Mismatch de payload entre `Event.payload` e `PayloadSchema`: o job deve refletir exatamente o payload publicado.
  - Misturar borda HTTP com job: job nao deve depender de semantica HTTP (status code/response); ele deve apenas executar a orquestracao do processamento assincrono.
  - Acessar `request.state` no job: job nao deve depender de request; job roda fora do ciclo HTTP.

# Regras de Integracao com Outras Camadas
- Dependencias permitidas e proibidas
  - `pubsub` pode depender de:
    - `core` (eventos e use cases).
    - `database` (repositorios SQLAlchemy concretos usados nos jobs).
    - `validation` (schemas Pydantic reutilizados para validar payload de evento).
    - SDK do Inngest (`inngest`).
  - `pubsub` nao deve depender de:
    - `routers` e `rest/controllers`.
    - Pipes (ex: `src/equiny/pipes/`) como dependencia interna de job.
- Contratos/interface de comunicacao
  - Publicacao de eventos deve acontecer via `Broker` (`src/equiny/core/shared/interfaces/broker.py`).
  - O adaptador `InngestBroker` deve traduzir `Event` (dominio) -> `inngest.Event` e enviar com `send_sync(...)`: `src/equiny/pubsub/inngest/inngest_broker.py`.
- Direcao de dependencia e limites de acoplamento
  - O `core` nao deve importar nada de `pubsub`.
  - O `rest` pode receber `Broker` via `Depends(PubSubPipe.get_broker)` e publicar eventos sem conhecer o SDK.
    - Pipe: `src/equiny/pipes/pubsub_pipe.py`.
    - Middleware que injeta client na request: `src/equiny/rest/middlewares/handle_inngest_client_middleware.py`.
    - Registro do Inngest e middlewares: `src/equiny/app.py`.

| De | Para | Tipo | Contrato | Arquivo real |
|---|---|---|---|---|
| `rest` | `pubsub` | `Depends` | `Broker` | `src/equiny/pipes/pubsub_pipe.py` |
| `rest` | `pubsub` | `middleware` | `request.state.inngest_client` | `src/equiny/rest/middlewares/handle_inngest_client_middleware.py` |
| `pubsub` | `core` | import | `Event`, `UseCase` | `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py` |
| `pubsub` | `database` | import | `Sqlalchemy*Repository` | `src/equiny/pubsub/inngest/jobs/profiling/create_owner_job.py` |

# Checklist Rapido para Novas Features na Camada
- Itens objetivos de validacao antes de abrir PR
  - Job novo esta em `src/equiny/pubsub/inngest/jobs/<contexto>/` e exportado em `__init__.py`.
  - Job valida payload com `PayloadSchema.model_validate(context.event.data)`.
  - Job usa `context.step.run(...)` para a acao principal.
  - Job usa `Job.sqlalchemy_session()` e nao faz commit/rollback manual.
  - Job chama `UseCase.execute(...)` e nao contem regra de negocio.
- Criterios minimos de conformidade arquitetural
  - Eventos consumidos/publicados sao do `core` (classe de evento, `name`, `payload`).
  - Publicacao de evento na borda usa `Broker` (porta), nao SDK do Inngest.
  - Nenhum import do `core` aponta para `pubsub`.
- Sinais de alerta para revisao tecnica
  - Job acessa Models ORM diretamente ou escreve SQL.
  - Job implementa validacao de dominio ou branching de negocio.
  - PayloadSchema nao bate com o evento publicado (campos ausentes/nomes divergentes).
  - Job depende de request/middleware/pipes (acoplamento indevido ao HTTP).

# Observacoes e Pendencias
- Premissas adotadas
  - A camada PubSub do projeto esta implementada via `Inngest` e registrada no `FastAPI` por `InngestPubSub.register(app)`.
  - A gestao transacional em jobs segue `Job.sqlalchemy_session()`.
- Informacoes ausentes
  - Padrao unificado de convencao para `fn_id` de jobs alem do exemplo atual (`profiling/create.owner.job`) nao esta documentado em regras; use o padrao ja existente para manter consistencia.
  - Nao ha (neste repositorio) um documento dedicado de retry/backoff/idempotencia por tipo de job; se isso virar recorrente, documentar um padrao explicito.
- Proximos passos para refinamento
  - Adicionar mais exemplos reais quando novos jobs forem criados (ex: outros contextos alem de `profiling`).
  - Se houver necessidade de padronizar `fn_id` e naming, criar convencao formal e aplicar de forma incremental.
