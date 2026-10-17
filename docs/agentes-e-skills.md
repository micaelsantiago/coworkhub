# Coworkhub: agentes e skills no OpenCode

Este documento descreve como usar os agentes especializados e as skills do projeto. O fluxo canônico de mudanças é o OpenSpec; agentes representam papéis com permissões estáveis, enquanto skills fornecem métodos específicos dentro desses papéis.

## 1. Conceitos

### Agente

Um agente define responsabilidade, instruções, permissões e capacidade de delegação. Por exemplo, o `agente-qa` pode ler e testar a aplicação, mas não pode editar arquivos.

Os agentes do projeto ficam em `.opencode/agents/`.

### Skill

Uma skill contém um processo reutilizável, como propor uma mudança OpenSpec, trabalhar em ciclos de TDD ou revisar uma interface. O agente carrega somente as skills permitidas para seu papel.

As skills do projeto ficam em `.agents/skills/`. Algumas são descobertas automaticamente pelo modelo; outras só entram quando são chamadas explicitamente.

### OpenSpec

O OpenSpec mantém a fonte de verdade de cada mudança:

- `proposal.md`: motivação e escopo;
- `specs/**/spec.md`: comportamento observável;
- `design.md`: decisões de implementação;
- `tasks.md`: trabalho e estado de conclusão.

Uma conversa, um ticket ou uma documentação auxiliar pode alimentar uma mudança, mas não substitui esses artefatos durante a implementação.

## 2. Agentes disponíveis

### Agentes de uso direto

| Agente | Quando usar | Pode editar | Skills principais |
|---|---|---|---|
| `agente-produto` | Problema ainda precisa de descoberta, validação ou decisões | Alterações pedem confirmação; não implementa produção | `openspec-explore`, `grilling`, `domain-modeling`, `codebase-design`, `research`, `prototype` |
| `agente-especificacao` | Criar, atualizar, sincronizar ou arquivar uma mudança | Somente `openspec/**` | `openspec-propose`, `openspec-update-change`, `openspec-sync-specs`, `openspec-archive-change` |
| `agente-backend` | Implementar domínio, dados, serviços, views, Celery e testes Django | Código, testes e tarefas da mudança | `openspec-apply-change`, `tdd`, `diagnosing-bugs`, `codebase-design`, `domain-modeling` |
| `agente-frontend` | Implementar templates, HTMX, Alpine, estilos, UX e texto de interface | Código, templates, assets, testes e tarefas da mudança | `openspec-apply-change`, `tdd`, `frontend-design`, `web-design-guidelines`, `copywriting`, `humanizer` |
| `agente-qa` | Revisar uma implementação contra padrões e especificação | Não; é read-only | `code-review`, `web-design-guidelines` |
| `agente-docs` | Escrever guias, ADRs, glossário, README ou comunicação de mudança | Documentação; arquivos de agentes pedem confirmação | `domain-modeling`, `humanizer`, `pr`, `writing-for-agents` |

Backend e frontend são separados por responsabilidade, não por uma fronteira rígida de diretórios. Uma entrega HTMX pode exigir mudanças coordenadas em views, forms e templates. As regras do domínio continuam no backend.

### Subagentes

| Subagente | Chamado por | Entrega |
|---|---|---|
| `agente-pesquisa` | `agente-produto`, por meio de `research` | Nota citada em `docs/research/` baseada em fontes primárias |
| `agente-qa-padroes` | `agente-qa`, por meio de `code-review` | Violações de padrões e riscos de regressão |
| `agente-qa-especificacao` | `agente-qa`, por meio de `code-review` | Divergências entre diff e artefatos OpenSpec |

Os subagentes recebem contexto novo e focado. O usuário normalmente escolhe um agente de uso direto; o agente responsável faz a delegação.

## 3. Fluxo canônico

```text
Ideia ou problema
      |
      v
agente-produto                  (descoberta, quando necessária)
      |
      v
agente-especificacao            (proposal + specs + design + tasks)
      |
      +--------------------+
      |                    |
      v                    v
agente-backend       agente-frontend
      |                    |
      +---------+----------+
                |
                v
           agente-qa
         /            \
        v              v
qa-padroes      qa-especificacao
         \            /
          +----------+
                |
                v
    correções no agente responsável
                |
                v
     agente-docs             (quando houver documentação)
                |
                v
 agente-especificacao        (sync e archive explícitos)
```

Nem toda mudança passa por todas as etapas. Descoberta pode ser dispensada quando o comportamento desejado já está claro. Documentação entra somente quando a mudança afeta material que usuários, operadores ou futuros desenvolvedores precisam consultar.

### 3.1 Descobrir

Use `agente-produto` quando ainda houver incerteza sobre problema, escopo, atores ou regras.

Exemplo:

```text
Use o agente-produto para investigar como reservas recorrentes deveriam
funcionar. Compare a ideia com o domínio e identifique decisões em aberto.
```

Saída esperada: fatos observados, decisões confirmadas, hipóteses e perguntas abertas. Quando houver pesquisa externa substancial, o agente delega ao `agente-pesquisa`.

### 3.2 Especificar

Use `agente-especificacao` quando a mudança já puder ser descrita em comportamento verificável.

```text
Use o agente-especificacao para propor a mudança de reservas recorrentes.
```

O agente cria os artefatos exigidos pelo schema ativo. Ele encerra depois do planejamento e não começa a implementação na mesma solicitação.

Se uma decisão mudar durante o trabalho:

```text
Use o agente-especificacao para atualizar a mudança de reservas recorrentes:
somente owners podem criar séries sem data final.
```

### 3.3 Implementar

Escolha o agente pela responsabilidade predominante:

```text
Use o agente-backend para aplicar a mudança de reservas recorrentes.
```

```text
Use o agente-frontend para aplicar as tarefas de interface da mudança de
reservas recorrentes.
```

Ambos usam `openspec-apply-change`, implementam tarefas focadas e marcam uma tarefa como concluída somente quando o comportamento especificado está completo. A verificação final é:

```sh
make lint
make test
```

Mudanças de model incluem migrations versionadas.

### 3.4 Revisar

Use `agente-qa` com um ponto fixo de comparação, normalmente `main`:

```text
Use o agente-qa para revisar esta mudança desde main.
```

O agente valida o diff e executa dois eixos em paralelo:

1. **Padrões:** compara a mudança com `AGENTS.md`, convenções do repositório e riscos arquiteturais.
2. **Especificação:** compara a mudança com proposal, specs, design e tasks do OpenSpec.

Achados não são corrigidos pelo QA. Eles voltam ao `agente-backend`, `agente-frontend` ou `agente-especificacao`, conforme a origem.

### 3.5 Documentar

Use `agente-docs` quando a mudança exigir documentação técnica, ADR, glossário, guia operacional ou texto de pull request.

```text
Use o agente-docs para documentar a nova regra de recorrência e preparar o
corpo da pull request.
```

O agente não altera código nem gerencia artefatos OpenSpec.

### 3.6 Sincronizar e arquivar

Depois da implementação e do QA, use `agente-especificacao` em ações separadas:

```text
Use o agente-especificacao para sincronizar as specs da mudança de reservas
recorrentes.
```

```text
Use o agente-especificacao para arquivar a mudança de reservas recorrentes.
```

Sincronizar atualiza as specs principais. Arquivar encerra a mudança. Nenhuma das ações é consequência automática da implementação.

## 4. Entradas rápidas

| Situação | Começar com | Caminho normal |
|---|---|---|
| Ideia vaga ou decisão de produto | `agente-produto` | Produto → Especificação → Implementação → QA |
| Requisito já claro | `agente-especificacao` | Especificação → Implementação → QA |
| Mudança OpenSpec pronta | `agente-backend` ou `agente-frontend` | Implementação → QA |
| Bug difícil ou regressão | Agente responsável pela área | `diagnosing-bugs` → correção → QA |
| Ajuste visual ou acessibilidade | `agente-frontend` | Implementação → QA |
| Revisão de branch ou PR | `agente-qa` | QA padrões + QA especificação |
| Pesquisa de documentação ou API | `agente-produto` | `research` → `agente-pesquisa` |
| ADR, guia ou glossário | `agente-docs` | Documentação |
| Sync ou archive de mudança | `agente-especificacao` | Ação OpenSpec explícita |

## 5. Catálogo de skills

O projeto possui 37 skills. Os grupos abaixo deixam claro quais participam do fluxo atual.

### 5.1 OpenSpec: ciclo canônico

| Skill | Uso |
|---|---|
| `openspec-explore` | Explorar uma ideia ou mudança sem implementar |
| `openspec-propose` | Criar proposta, specs, design e tarefas |
| `openspec-update-change` | Revisar artefatos existentes e manter coerência |
| `openspec-apply-change` | Implementar e acompanhar as tarefas |
| `openspec-sync-specs` | Levar deltas aprovados para as specs principais |
| `openspec-archive-change` | Arquivar uma mudança concluída |

### 5.2 Técnicas de engenharia

| Skill | Uso |
|---|---|
| `tdd` | Implementação em ciclos red-green-refactor |
| `diagnosing-bugs` | Diagnóstico baseado em um loop reproduzível |
| `code-review` | Revisão independente de padrões e especificação |
| `codebase-design` | Vocabulário e critérios para módulos profundos e seams testáveis |
| `domain-modeling` | Glossário, cenários de domínio e ADRs |
| `prototype` | Protótipo descartável para responder uma pergunta de design |
| `research` | Delegação de pesquisa baseada em fontes primárias |
| `pr` | Estrutura do corpo de uma pull request |
| `retro` | Retrospectiva da sessão e melhoria do ambiente de engenharia |

### 5.3 Interface e texto

| Skill | Uso |
|---|---|
| `frontend-design` | Direção visual e construção de interfaces intencionais |
| `web-design-guidelines` | Revisão de UX, acessibilidade e práticas de interface |
| `copywriting` | Criação ou reformulação de texto de produto |
| `humanizer` | Revisão de texto existente para remover padrões artificiais |

### 5.4 Colaboração e operações manuais

| Skill | Uso |
|---|---|
| `grilling` | Entrevista rigorosa para testar decisões |
| `grill-me` | Entrevista sem persistência no repositório |
| `grill-with-docs` | Entrevista que também atualiza glossário e ADRs |
| `handoff` | Contexto portátil para outra sessão, diretório ou pessoa |
| `to-questionnaire` | Questionário para obter decisões de terceiros |
| `teach` | Aprendizado guiado dentro do workspace |
| `wait-what` | Reformulação de uma explicação que não ficou clara |
| `wizard` | Script interativo para etapas que exigem ação humana |
| `writing-for-agents` | Escrita e manutenção de skills, `AGENTS.md` e documentos para agentes |

### 5.5 Fluxo legado estacionado

Estas skills continuam instaladas, mas não fazem parte das permissões dos agentes OpenSpec:

- `ask-matt`;
- `setup-matt-pocock-skills`;
- `to-spec`;
- `to-tickets`;
- `implement`;
- `implement-spec`;
- `triage`;
- `wayfinder`;
- `improve-codebase-architecture`.

Elas formam ou dependem de um segundo fluxo baseado em issue tracker. Misturá-las ao ciclo OpenSpec criaria duas fontes para requisitos, tarefas e conclusão. Uma skill desse grupo só deve voltar ao fluxo principal depois de ser adaptada explicitamente ao OpenSpec.

## 6. Permissões e segurança

- `agente-qa` e seus subagentes são read-only.
- `agente-especificacao` edita somente `openspec/**`.
- `agente-docs` não edita implementação nem artefatos OpenSpec.
- `agente-pesquisa` escreve somente em `docs/research/`.
- Acesso fora do projeto pede confirmação.
- `git push` sempre pede confirmação explícita antes de executar.
- Segredos ficam em variáveis de ambiente ou mecanismos de autenticação, nunca em prompts, documentação ou arquivos versionados.

Permissões são barreiras técnicas, mas não substituem a revisão humana de migrations, segurança multi-tenant e ações operacionais irreversíveis.

## 7. Onde manter cada parte

| Arquivo ou diretório | Responsabilidade |
|---|---|
| `.opencode/agents/*.md` | Papéis, prompts e permissões dos agentes |
| `.opencode/opencode.jsonc` | Regras compartilhadas do OpenCode no projeto |
| `.agents/skills/*/SKILL.md` | Processos reutilizáveis |
| `openspec/config.yaml` | Contexto e regras aplicadas aos artefatos OpenSpec |
| `openspec/changes/` | Mudanças em planejamento ou implementação |
| `openspec/specs/` | Especificações principais já sincronizadas |
| `AGENTS.md` | Instruções sempre carregadas sobre o repositório |
| `docs/` | Produto, domínio, arquitetura e operação |

Ao criar ou alterar um agente, uma skill ou `AGENTS.md`, carregue `writing-for-agents`. Evite copiar regras entre arquivos: mantenha uma fonte de verdade e use apontadores claros para alcançá-la.
