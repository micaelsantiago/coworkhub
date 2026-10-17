# Coworkhub: documentação do projeto

Esta pasta concentra o contexto de produto, domínio, arquitetura, operação e fluxo de desenvolvimento do Coworkhub.

## Resumo

O Coworkhub é um SaaS B2B multi-tenant para coworkings pequenos e médios. A primeira versão ajuda a equipe a organizar a operação e permite que membros reservem salas e mesas sem depender de planilhas ou conversas dispersas.

Cada empresa de coworking é um tenant e pode possuir uma ou mais unidades. O modelo comercial inicial previsto é uma mensalidade por unidade.

## Documentos

| Documento | Conteúdo |
|---|---|
| [`produto.md`](produto.md) | Visão, público, proposta de valor, atores e objetivos |
| [`mvp.md`](mvp.md) | Escopo da primeira versão, jornadas e critérios de sucesso |
| [`dominio.md`](dominio.md) | Vocabulário, entidades e regras centrais do negócio |
| [`arquitetura.md`](arquitetura.md) | Decisões de software e organização da aplicação |
| [`infraestrutura.md`](infraestrutura.md) | Hospedagem, segurança, backup e operação |
| [`agentes-e-skills.md`](agentes-e-skills.md) | Agentes especializados, catálogo de skills e fluxo OpenSpec |
| [`fluxo-de-desenvolvimento.md`](fluxo-de-desenvolvimento.md) | Branches semânticas, sandbox, promoção e produção |
| [`adr/`](adr/0001-planos-operacionais-e-livro-razao.md) | Registros de Decisões de Arquitetura (ADRs) |

## Decisões já tomadas

- Público inicial: coworkings pequenos e médios.
- Problema central: reservas e operação diária.
- Usuários e papéis da primeira versão: 3 papéis fixos (`owner`, `staff` e `member`), simplificando o MVP. O papel `staff` suporta escopo restrito por filial.
- Filiais: cadastradas como unidades (`Units`) sob o mesmo `Tenant`, compartilhando membros, marca e subdomínio único.
- Recursos reserváveis no MVP: salas e mesas (ambos como recursos exclusivos numerados).
- Reservas confirmadas automaticamente com proteção de concorrência no PostgreSQL via `ExclusionConstraint` (`btree_gist` e `tstzrange`).
- Entrada de membros por cadastro ou convite da equipe, sem cadastro público aberto.
- Onboarding do coworking self-service no portal raiz (`coworkhub.com.br`) com geração automática do subdomínio a partir do nome definido pelo usuário (ex: "Estação Coworking" → `estacao-coworking.coworkhub.com.br`).
- Assinatura do SaaS (`platform_billing`) via gateway **Asaas** com padrão Adapter/Gateway Interface, período de trial de 7 dias e validação prévia de cartão de crédito no signup.
- Planos operacionais dos membros baseados em franquias mensais de horas, controlados por ledger imutável de `CreditMovement` (cobrança dos membros permanece externa no MVP).
- Aplicação: monolito Django com templates, HTMX, Alpine.js e Tailwind CSS.
- Multi-tenancy: banco único com isolamento em profundidade (Manager Fail-Closed, FK Composta, Row-Level Security no Postgres e ContextVar seguro).
- Autenticação e Sessões: login global por e-mail com cookie compartilhado `.dominio.com.br` e autorização estrita por `Membership` ativa no subdomínio.
- Infraestrutura: VPS Contabo (8 GB RAM) com limites rígidos de contêineres (~5.5 GB alocados), swap de 2 GB, Cloudflare Tunnel e backups automatizados no Cloudflare R2 (RPO <= 1h, RTO <= 2h).

## Convenções da documentação

- **MVP** indica compromisso da primeira versão utilizável por clientes.
- **Futuro** indica uma possibilidade, não um compromisso de entrega.
- **Em aberto** indica uma decisão que precisa de validação de produto ou técnica.
- Valores comerciais, limites e prazos não devem ser assumidos sem validação.

## Próximos refinamentos e implementação

1. Entrevistar operadores de 3 a 5 coworkings do público-alvo para validação final de UX/telas.
2. Definir métricas de baseline da operação atual dos clientes-piloto.
3. Inicializar repositório de código e ambiente Docker Compose local (Postgres 16 + Redis + Django).
4. Implementar apps fundamentais: `core` (`TenantModel`, Manager Fail-Closed), `tenants` (middleware e contexto) e `accounts` (`User` customizado e `Membership`).
5. Construir o harness de testes automatizados de isolamento (`TenantIsolationTestCase`).
