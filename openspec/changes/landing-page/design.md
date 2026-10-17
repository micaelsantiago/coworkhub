## Context

A aplicação Coworkhub é um monólito Django 5.2 server-rendered estruturado com HTMX, Alpine.js e Tailwind CSS v4. Conforme `docs/arquitetura.md`, o acesso ao host institucional (`coworkhub.com.br` ou `localhost:8000`) opera com `request.tenant = None` (sem tenant ativo no contexto), sendo a rota pública da plataforma.

A página inicial atual em `templates/home.html` atua apenas como verificação de ambiente local. Esta mudança implementa a interface pública e os seletores/views necessários para apresentar o produto e permitir a validação antecipada do subdomínio para cadastro de novos tenants.

## Goals / Non-Goals

**Goals:**
- Servir a landing page institucional de alta conversão em `GET /` sem dependência de tenant.
- Criar a view e o endpoint `POST /check-subdomain/` com validação síncrona no backend e feedback assistivo via HTMX no frontend.
- Implementar as regras de normalização de slug (`django.utils.text.slugify`) e lista de subdomínios reservados (`RESERVED_SUBDOMAINS`).
- Utilizar a paleta de cores e tipografia oficiais do projeto configuradas em `assets/css/input.css` (`primary: #b85c38`).
- Criar testes automatizados cobrindo a view da landing page e os cenários de validação de subdomínio.

**Non-Goals:**
- Implementar o fluxo completo de checkout e validação de cartão de crédito no gateway Asaas (objeto de mudança separada de Onboarding/Platform Billing).
- Criar o provisionamento definitivo de `Tenant` e `Domain` no banco de dados (será acionado pelo formulário completo de onboarding).
- Criar telas autenticadas de membros ou painéis operacionais do coworking nesta etapa.

## Decisions

### 1. Localização e Responsabilidade do Endpoint de Validação
- **Decisão:** O endpoint `/check-subdomain/` e a view da landing page ficam em `apps.core.views` ou utilizam helpers de domínio de `apps.tenants` (mantendo validação autoritativa).
- **Alternativa considerada:** Colocar a validação apenas no frontend via regex em Alpine.js.
- **Justificativa:** O backend deve ser autoritativo. Mesmo que o HTMX forneça feedback instantâneo na digitação, a lista de termos reservados (`RESERVED_SUBDOMAINS`) e a unicidade futura de domínio precisam ser garantidas no servidor.

### 2. Formato da Resposta do HTMX
- **Decisão:** O endpoint `/check-subdomain/` renderiza um fragmento HTML parcial (`templates/components/subdomain_check_result.html`). Se a requisição não for HTMX, retorna uma resposta limpa ou estruturada.
- **Alternativa considerada:** Retornar JSON e processar no cliente via Alpine.js.
- **Justificativa:** Mantém a consistência da arquitetura server-rendered com HTMX estabelecida no projeto, simplificando o estado do frontend.

### 3. Termos Reservados de Subdomínio
- **Decisão:** Definir lista canônica `RESERVED_SUBDOMAINS = {"www", "app", "admin", "api", "status", "mail", "billing", "webhook", "suporte", "help", "static", "media"}` em consonância com `docs/arquitetura.md`.
- **Alternativa considerada:** Deixar para validar apenas na inserção no banco de dados.
- **Justificativa:** Evita que o usuário visualize um subdomínio como válido no Hero e tenha seu cadastro rejeitado posteriormente no onboarding.

### 4. Modularização dos Templates
- **Decisão:** A landing page será implementada em `templates/pages/landing.html`, herdando de `templates/base.html`, com seções organizadas ou incluídas de forma semântica, reaproveitando os componentes existentes em `templates/components/` (`button.html`, `badge.html`, etc.).

## Risks / Trade-offs

- **[Risco] Validação de subdomínio no Hero sugerir que o slug já foi reservado de forma persistente:**
  - *Mitigação:* A mensagem de feedback indica claramente que o subdomínio está *disponível*, mas o registro efetivo ocorre apenas na conclusão do cadastro/onboarding.
- **[Risco] Concorrência caso dois usuários tentem o mesmo subdomínio simultaneamente no onboarding final:**
  - *Mitigação:* A constraint de unicidade no banco de dados no momento da criação do `Domain` é a autoridade final (`docs/arquitetura.md`).
