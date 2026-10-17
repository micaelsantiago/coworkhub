# Coworkhub: fluxo de desenvolvimento e branches

Este documento define como uma mudança sai da `main`, passa pelo sandbox e chega à produção. O fluxo vale para features, correções, refatorações, documentação e manutenção.

## 1. Papel das branches permanentes

| Branch | Papel | Ambiente |
|---|---|---|
| `main` | Fonte de verdade da produção e origem de toda branch de trabalho | Produção |
| `develop` | Integração temporária e validação das mudanças | Sandbox |

A `develop` não é a origem de features. Toda branch de trabalho nasce da `main` atualizada. Assim, o pull request final para produção contém somente a mudança pretendida, sem carregar outras features que estejam no sandbox.

As duas branches permanentes devem ser protegidas. Alterações entram por pull request; não há commits ou pushes diretos.

### 1.1 Preparar a `develop`

Antes do primeiro ciclo, um mantenedor cria a `develop` a partir da `main` atualizada e publica a branch:

```sh
git switch main
git pull --ff-only origin main
git switch -c develop
git push -u origin develop
```

Esse push é o bootstrap da branch permanente. Depois dele, a `develop` recebe mudanças somente por pull request.

No provedor Git:

- proteja `main` e `develop` contra push direto;
- exija CI e revisão antes do merge conforme a maturidade do projeto;
- não apague automaticamente a branch de origem quando um PR for integrado à `develop`, pois a mesma branch ainda abrirá o PR para `main`;
- mantenha `main` como branch padrão do repositório.

## 2. Branches semânticas

Use nomes em kebab-case, curtos e associados ao comportamento entregue:

| Prefixo | Uso | Exemplo |
|---|---|---|
| `feat/` | Nova capacidade | `feat/reservas-recorrentes` |
| `fix/` | Correção de defeito | `fix/conflito-de-horario` |
| `hotfix/` | Correção urgente de produção | `hotfix/login-indisponivel` |
| `refactor/` | Mudança interna sem alterar comportamento esperado | `refactor/servico-de-reservas` |
| `perf/` | Melhoria de desempenho | `perf/consulta-de-disponibilidade` |
| `docs/` | Documentação | `docs/fluxo-de-deploy` |
| `test/` | Cobertura ou infraestrutura de testes | `test/isolamento-de-tenant` |
| `chore/` | Manutenção de projeto ou dependências | `chore/atualizar-django` |
| `ci/` | Pipeline e automação | `ci/publicar-imagem` |

O prefixo descreve a mudança predominante. Não use nome de pessoa, número isolado ou termos genéricos como `ajustes` e `mudancas`.

## 3. Fluxo completo

```text
main atualizada
      |
      | cria feat/*, fix/*, refactor/*, ...
      v
branch de trabalho
      |
      | implementação + microcommits + QA
      v
PR: branch de trabalho -> develop
      |
      | merge commit
      v
develop / sandbox
      |
      | testes funcionais e técnicos
      | correções continuam na branch de trabalho
      v
PR: mesma branch de trabalho -> main
      |
      | merge commit
      v
main / produção
      |
      | smoke test e confirmação
      v
sincronizar main -> develop
      |
      v
apagar branch de trabalho
```

### 3.1 Criar a branch

Atualize a `main` local antes de criar qualquer trabalho:

```sh
git switch main
git pull --ff-only origin main
git switch -c feat/reservas-recorrentes
```

Uma mudança OpenSpec deve estar clara o suficiente para implementação antes desta etapa. O nome da branch e o nome da mudança podem compartilhar o mesmo slug quando isso facilitar a rastreabilidade.

### 3.2 Implementar

Trabalhe somente na branch criada. Organize o histórico em microcommits semânticos usando Conventional Commits:

```text
feat(bookings): adicionar modelo de recorrencia
test(bookings): cobrir conflitos entre ocorrencias
docs(bookings): explicar limites de recorrencia
```

Cada commit deve representar uma unidade coerente, manter o projeto em estado compreensível e evitar misturar refatoração não relacionada com comportamento novo.

Antes do primeiro pull request:

1. conclua as tarefas OpenSpec incluídas no escopo;
2. execute `make lint` e `make test`;
3. revise o diff da branch contra `main` com o `agente-qa`;
4. corrija os achados no agente responsável;
5. envie a branch somente após confirmação explícita de push.

### 3.3 Validar no sandbox

Abra o primeiro pull request:

```text
branch de trabalho -> develop
```

Faça o merge com **merge commit**. Não apague a branch, pois ela ainda será a origem do pull request para `main`.

Depois do deploy da `develop` no sandbox:

1. confirme qual SHA da branch foi implantado;
2. execute os cenários funcionais da especificação;
3. execute smoke tests das jornadas afetadas;
4. verifique migrations, tarefas assíncronas, logs e isolamento de tenant quando aplicáveis;
5. registre o resultado no pull request ou na mudança OpenSpec.

A `develop` pode conter outras mudanças ainda não promovidas. A aprovação deve identificar o SHA testado e distinguir defeitos da feature de problemas causados pela combinação presente no sandbox.

### 3.4 Corrigir problemas encontrados no sandbox

Não corrija diretamente na `develop`. Volte para a branch de trabalho, faça os commits necessários e envie-os.

Como o primeiro pull request para `develop` já pode estar merged, commits posteriores entram por um novo pull request da mesma branch para `develop`. Repita o teste de sandbox até que o SHA mais recente seja aprovado.

Se a mudança precisar sair do sandbox antes de ficar pronta, reverta o merge na `develop`. Preserve a branch de trabalho para correção; não abra o pull request para `main`.

### 3.5 Promover para produção

Depois da aprovação no sandbox, abra o segundo pull request usando a mesma branch:

```text
branch de trabalho -> main
```

O pull request deve informar:

- mudança OpenSpec correspondente;
- SHA validado no sandbox;
- resultado de `make lint` e `make test`;
- cenários funcionais executados;
- migrations, riscos operacionais e estratégia de reversão, quando aplicáveis;
- confirmação de que todos os commits testados estão incluídos.

Faça o merge com **merge commit**. Usar os mesmos commits nos dois pull requests preserva ancestralidade comum entre `main`, `develop` e a branch de trabalho. Evite squash ou rebase no momento do merge, pois eles criam commits diferentes para a mesma mudança e dificultam a sincronização posterior.

### 3.6 Confirmar produção e encerrar

Depois do deploy da `main`:

1. execute um smoke test em produção;
2. confirme que métricas, logs e jobs relevantes estão saudáveis;
3. sincronize e arquive a mudança OpenSpec;
4. leve `main` de volta para `develop` por pull request, incorporando o merge de produção e eventuais hotfixes;
5. apague a branch de trabalho local e remota.

A branch só é descartada depois que a mudança estiver integrada à `main` e confirmada em produção. Nesse ponto, o conteúdo da feature está presente tanto em `main` quanto em `develop`.

## 4. Estratégia de merge

Para este fluxo, os pull requests da branch de trabalho para `develop` e para `main` usam **merge commit**.

Essa decisão permite que:

- os microcommits semânticos sejam preservados;
- o mesmo conjunto de commits seja testado e promovido;
- Git reconheça a ancestralidade compartilhada ao sincronizar `main` com `develop`;
- a branch continue aberta depois da integração no sandbox.

Não force push depois que uma branch tiver sido enviada para revisão. Correções entram como novos commits. Rebase é aceitável somente antes do primeiro push, enquanto a branch ainda não for compartilhada.

## 5. Sincronização entre `main` e `develop`

O sentido regular de sincronização é:

```text
main -> develop
```

Nunca use `develop` como fonte para atualizar uma branch de trabalho ou para promover em bloco tudo que está no sandbox. Cada feature chega à `main` pelo seu próprio pull request.

Depois de cada promoção confirmada em produção, abra um pull request de `main` para `develop`. Isso mantém na sandbox os merge commits de produção, hotfixes e demais mudanças operacionais sem promover acidentalmente features pendentes para a `main`.

Se houver conflito nessa sincronização, resolva-o em uma branch auxiliar criada a partir de `develop`, preserve o comportamento de produção e valide novamente o sandbox.

## 6. Relação com OpenSpec e agentes

| Etapa Git | OpenSpec | Agente principal |
|---|---|---|
| Descobrir a mudança | Exploração | `agente-produto` |
| Planejar | Proposal, specs, design e tasks | `agente-especificacao` |
| Criar branch da `main` | Mudança pronta para apply | `agente-backend` ou `agente-frontend` |
| Implementar | Atualizar tasks durante o apply | `agente-backend` ou `agente-frontend` |
| Revisar antes da sandbox | Comparar branch com `main` | `agente-qa` |
| Validar na `develop` | Registrar evidências | Responsável pela mudança |
| Corrigir | Manter tasks e design coerentes | Agente da área |
| Promover para `main` | Todos os requisitos atendidos | Responsável pela mudança |
| Documentar | Atualizar guias e ADRs necessários | `agente-docs` |
| Encerrar em produção | Sync e archive | `agente-especificacao` |

O fluxo de agentes e skills está detalhado em [`agentes-e-skills.md`](agentes-e-skills.md).

## 7. Checklist resumido

### Branch de trabalho

- [ ] Criada a partir da `main` atualizada.
- [ ] Nome semântico e em kebab-case.
- [ ] Microcommits semânticos e focados.
- [ ] `make lint` e `make test` aprovados.
- [ ] Revisão do `agente-qa` concluída contra `main`.

### Sandbox

- [ ] PR da branch para `develop` integrado com merge commit.
- [ ] SHA implantado registrado.
- [ ] Cenários funcionais e smoke tests aprovados.
- [ ] Correções feitas na branch de trabalho, não na `develop`.

### Produção

- [ ] PR da mesma branch para `main` integrado com merge commit.
- [ ] Smoke test de produção aprovado.
- [ ] `main` sincronizada de volta em `develop`.
- [ ] Mudança OpenSpec sincronizada e arquivada.
- [ ] Branch de trabalho removida local e remotamente.
