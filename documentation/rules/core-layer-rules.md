# Regras da camada Core

## Visao geral e modulos da camada

A camada `src/equiny/core/` representa o nucleo de negocio da aplicacao.
Ela concentra regras de dominio, contratos e orquestracao de casos de uso,
sem acoplamento com HTTP, ORM ou banco de dados.

Modulos atuais:

- `shared`: shared kernel com abstracoes, estruturas base, erros e decorators.
- `auth`: contexto de autenticacao (entidade `Account`, DTO, evento e use case).
- `profiling`: contexto de perfil de cavalo (entidade `Horse`, estruturas,
  erros, interface de repositorio e use cases).

Responsabilidade de alto nivel:

- modelar o negocio com tipos ricos e invariantes;
- definir contratos estaveis para integracao com outras camadas;
- oferecer casos de uso como ponto de entrada para operacoes de dominio.

## Estrutura de diretorios explicada

```text
src/equiny/core/
  auth/
    domain/
      entities/
        dtos/
      events/
    use_cases/
  profiling/
    domain/
      entities/
        dtos/
      structures/
      errors/
    interfaces/
      repositories/
    use_cases/
  shared/
    domain/
      abstracts/
      decorators/
      errors/
      structures/
```

Leitura por responsabilidade:

- `domain/entities`: entidades com identidade e comportamento de negocio.
- `domain/entities/dtos`: contratos de entrada/saida entre casos de uso e bordas.
- `domain/structures`: value objects e enums com regras de validacao.
- `domain/errors`: erros especificos do contexto, estendendo erros base.
- `domain/events`: eventos de dominio.
- `interfaces/repositories`: portas de saida (contratos para persistencia).
- `use_cases`: orquestracao de fluxo de negocio, sem dependencia de infraestrutura.
- `shared/domain/*`: tipos e regras comuns reutilizadas pelos contextos.

## Principios Fundamentais

### ✅ O que DEVE conter

- Regras de negocio puras e invariantes de dominio.
- Entidades, estruturas e DTOs claros, com tipagem explicita.
- Casos de uso orientados a intencao (`execute(...)`) e focados em fluxo.
- Interfaces de repositorio abstratas (ports), nunca implementacoes concretas.
- Erros de dominio (`AppError` e derivados) para sinalizar violacoes de regra.
- Fabrica de objetos via metodos `create(...)` para centralizar validacao.

### ❌ O que NUNCA deve conter

- Imports de FastAPI, SQLAlchemy, ORM, HTTP client, filas, cache ou broker.
- Regras de serializacao HTTP (status code, request/response, Depends).
- Acesso direto a env vars, sessao de banco ou detalhes de transacao.
- Dependencia em repositorio concreto de infraestrutura.
- Logica de mapeamento para modelo de banco dentro de entidade/use case.

## Glossario arquitetural

### Entidades

Objeto de dominio com identidade estavel (`id`) e igualdade por identidade.
No projeto, `Entity` define `__eq__` baseado em `id` e o decorator `@entity`
padroniza entidades como dataclasses mutaveis (`kw_only=True`, `eq=False`).

Exemplos: `Account`, `Horse`.

### DTOs

Objetos de transferencia de dados para cruzar fronteiras entre camadas.
No projeto, DTOs usam `@dto` e carregam dados de entrada/saida de use cases.
Nao devem conter regra de negocio complexa.

Exemplos: `AccountDto`, `HorseDto`.

### Interfaces

Contratos abstratos que descrevem dependencias externas da regra de negocio.
No projeto, `HorsesRepository` e a porta usada por use cases para persistir
e buscar `Horse`, sem conhecer SQLAlchemy.

### Use Cases

Aplicacao de regras em fluxos especificos da aplicacao.
Recebem dependencias por construtor (injeccao por interface), coordenam
entidades/estruturas e retornam DTOs.

Exemplos: `CreateHorseUseCase`, `GetHorseUseCase`, `SignInAccountUseCase`.

### Decorators

Decorators de modelagem (`@entity`, `@structure`, `@dto`) encapsulam padrao de
declaracao com `pydantic.dataclasses` e reduzem boilerplate.

- `@entity`: mutavel, keyword-only, igualdade custom por identidade.
- `@structure`: imutavel, comparacao por valor.
- `@dto`: contrato leve para transporte de dados.

## Padroes de projeto e Padroes de uso aplicados

Padroes arquiteturais observados:

- Clean/Hexagonal style: `core` define regras e portas; adaptadores vivem fora.
- DDD tatico: Entities, Value Objects (Structures), Domain Errors e Events.
- Repository pattern: use case depende de interface (`HorsesRepository`).
- Data Mapper: camada `database/sqlalchemy/mappers` converte entidade <-> modelo.
- Factory Method: criacao via `create(...)` em entidades e estruturas.
- Error Hierarchy: especializacao de erro por contexto (`HorseNotFoundError`).

Padroes de uso no fluxo atual:

1. Entrada chega por schema na borda REST.
2. Schema converte para DTO (`to_dto()`).
3. Use case cria/consulta entidade via interface de repositorio.
4. Entidade retorna DTO por propriedade `dto`.
5. Camadas externas serializam resposta.

Observacao de estado atual (importante para evolucao):

- `Horse.create(...)` define `Breed` como arabe fixo, ignorando `dto.breed`.
- `Name.create(...)` levanta `pydantic.ValidationError`, enquanto o restante da
  camada usa `core.shared.domain.errors.ValidationError`.
- `SignInAccountUseCase` retorna `AccountDto` diretamente sem persistencia/autenticacao.

## Convencoes de nomenclatura

Convencoes observadas e recomendadas:

- Diretorios e arquivos em `snake_case`.
- Classes em `PascalCase`.
- Sufixos explicitos por papel:
  - `*UseCase`
  - `*Repository`
  - `*Dto`
  - `*Error`
  - `*Event`
- Metodos de fabrica estaticos chamados `create(...)`.
- Metodo principal de caso de uso chamado `execute(...)`.
- Propriedade de serializacao de entidade chamada `dto`.
- Enums com nomes em `UPPER_SNAKE_CASE` (ex.: `BreedValue`).
- Exposicao publica de modulo via `__init__.py` + `__all__`.

## Regras de integracao com outras camadas da aplicacao

Direcao de dependencias obrigatoria:

- `rest/controllers` -> `core/use_cases`
- `core/use_cases` -> `core/interfaces` e `core/domain`
- `database/repositories` -> implementa `core/interfaces`
- `database/mappers` -> traduz tipos de persistencia para tipos de dominio

Regras de integracao por camada:

### Integracao com REST (`src/equiny/rest/`)

- Controller recebe request e delega para use case.
- Controller instancia adaptador concreto (ex.: repositorio SQLAlchemy) e injeta
  no use case por interface.
- `response_model` deve usar DTO do `core`, nunca entidade/modelo ORM.
- Erros de dominio devem ser traduzidos para HTTP na borda (handler/exception map).

### Integracao com Validation (`src/equiny/validation/`)

- Schemas validam formato e limites de entrada.
- Conversao para DTO e feita antes de chamar use case.
- Regras de negocio continuam no `core`, mesmo quando schema ja valida campos.

### Integracao com Database (`src/equiny/database/`)

- Implementacoes de repositorio devem aderir exatamente ao contrato da interface.
- Mapper e responsavel por conversoes entidade <-> modelo de banco.
- Sessao/transacao fica fora do `core` (middleware e infra).

### Integracao com Routers/Middlewares (`src/equiny/routers/`, `src/equiny/middlewares/`)

- Composicao de rotas, prefixos e DI de sessao acontecem fora do `core`.
- `core` nao conhece request lifecycle nem commits/rollback.

Checklist rapido para novas features no `core`:

1. Criar tipos de dominio (`entities`, `structures`, `errors`, `events`) no contexto.
2. Definir portas em `interfaces` para dependencias externas.
3. Implementar `use_cases` com retorno em DTO.
4. Expor contratos em `__init__.py`.
5. Integrar na borda (REST/DB) sem inverter dependencias.
