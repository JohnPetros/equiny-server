---
description: Criar bug report estruturado a partir de um relato inicial
---

# Prompt: Criar Bug Report

**Objetivo:**
Transformar um esboço ou relato informal de um erro em um **Bug Report Profissional**, padronizado e pronto para ser entregue à equipe de desenvolvimento.

**Entrada:**
* **Esboço do Problema:** documento de report com apenas o problema descrito de maneira geral
* **Contexto Técnico (Opcional):** [Inserir info do dispositivo, OS, versão do app, se houver]

**Diretrizes de Execução:**

1.  **Análise do Relato:** Interprete o esboço do problema e o contexto técnico fornecido.
2. Entenda a arquitetura do projeto, usando as guidelines de cada camada.
3.  **Diagnóstico:** Identifique as prováveis causas com base na arquitetura do sistema descrito em documentation\architecture.md. Para maior compreendimento do contexto da funcionalidade, se existir, veja o PRD da funcionalidade afetada, localizada no root do diretorio de bug-reports, no nível acima
4.  **Mapeamento de Camadas:** Determine quais camadas (UI, Core, REST, Drivers) e arquivos específicos estão envolvidos.
5.  **Plano de Correção:** Elabore uma solução passo a passo, separada por camadas, para orientar o desenvolvimento.

**Formato de Saída Obrigatório:**

Por favor, gere a resposta dentro de um bloco de código Markdown seguindo estritamente este template:

```markdown
## 🐛 Bug Report: [Título Curto e Descritivo]

**Problema Identificado:**
[Uma frase clara descrevendo o comportamento inesperado]

**Causas:**
[Explicação sucinta das possíveis razões técnicas para o erro]

**Contexto e Análise:**
### [Nome da Camada (ex: Camada UI, Camada Core, Camada REST, Camada Drivers)]

<!-- Repita o bloco abaixo para cada camada afetada -->
- Arquivo: `[Caminho/Nome do Arquivo]`
- Diagnóstico: [O que está errado especificamente neste local]

**Plano de Correção (Spec):**

### 1. O que já existe? (Contexto/Impacto)
Liste recursos da codebase (Services, Widgets, DTOs, Stores, Drivers, etc.) que serão utilizados ou impactados. Indique caminhos absolutos ou relativos claros.

- **[Camada]**: 
[Nome do Componente] - [Responsabilidade]
[Nome do Componente] - [Responsabilidade]

### 2. O que deve ser criado?
Descreva novos componentes necessários para a correção.

- **[Camada]**: 
[Nome do Componente] - [Responsabilidade]
[Nome do Componente] - [Responsabilidade]

### 3. O que deve ser modificado?
Liste as alterações em código existente.

- **[Camada]**: 
[Nome do Componente] - [Responsabilidade]
[Nome do Componente] - [Responsabilidade]

### 4. O que deve ser removido?
Liste código legado ou refatorações de limpeza necessárias (se houver).

- **[Camada]**: 
[Nome do Componente] - [Responsabilidade]
[Nome do Componente] - [Responsabilidade]
