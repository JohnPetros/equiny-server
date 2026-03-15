# PRD - Cadastro e login com Google

- Status: concluido
- Ultima atualizacao: 2026-03-15
- Milestone de referencia: `https://github.com/JohnPetros/equiny/milestone/12`

## Objetivo de produto

Reduzir friccao no primeiro acesso permitindo que o usuario entre com a conta Google e receba sessao autenticada imediatamente, sem depender de criacao manual de senha ou verificacao de email no fluxo social.

## Entrega consolidada

- [x] Usuário pode entrar ou se cadastrar com Google usando um unico endpoint de auth.
- [x] Contas Google novas entram verificadas automaticamente e seguem para o onboarding sem etapa adicional de email.
- [x] Contas existentes com o mesmo email sao reaproveitadas sem duplicidade de cadastro.
- [x] O vinculo social passa a ser persistido de forma estruturada, preparando a base para expansao futura de login social.
- [x] Tentativas de login por senha em contas exclusivamente sociais retornam orientacao clara para usar o Google.

## Impacto esperado

- Menor abandono no cadastro inicial.
- Menos suporte relacionado a senha e verificacao de email para usuarios que preferem login social.
- Melhor continuidade entre autenticacao e onboarding, com sessao pronta logo apos a validacao do Google.

## Fora desta entrega

- Apple/Facebook e outros provedores sociais.
- Gestao de contas vinculadas.
- Refresh token OAuth do Google.
