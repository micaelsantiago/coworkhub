## Why

O Coworkhub atualmente possui apenas uma página de boas-vindas do ambiente local (`templates/home.html`) sem apresentação do produto, proposta de valor ou fluxo de entrada para novos clientes.

Para validar o posicionamento de mercado e viabilizar a aquisição de novos tenants conforme descrito em `docs/produto.md` e `docs/mvp.md`, a aplicação precisa de uma landing page institucional no domínio raiz (`coworkhub.com.br` / `localhost:8000`). A página deve comunicar claramente a solução de reservas e autoatendimento para coworkings pequenos e médios, além de permitir a validação interativa antecipada do subdomínio do futuro tenant via HTMX.

## What Changes

- **Landing Page Institucional:** Substituição da página de demonstração técnica por uma landing page de alta conversão estruturada em seções: Hero com call-to-action e visual do produto, contraste operacional ("hoje vs. com Coworkhub"), pilares de funcionalidades do MVP, onboarding em 3 passos, preços/trial transparente, FAQ interativo com Alpine.js e rodapé institucional.
- **Validação Interativa de Subdomínio:** Endpoint público (`/check-subdomain/`) que normaliza nomes (`slugify`), valida regras de formatação e colisão com termos reservados (`RESERVED_SUBDOMAINS`), retornando feedback visual imediato para o HTMX no Hero.
- **Integração de Design e Componentes:** Estilização com a paleta do projeto em Tailwind CSS v4 (`primary` `#b85c38`), respeitando acessibilidade, contraste e microinterações de interface.

## Capabilities

### New Capabilities
- `landing-page`: Apresentação institucional do produto Coworkhub, comunicação da proposta de valor para donos de coworking e validação assistiva de subdomínio para início do fluxo de onboarding.

### Modified Capabilities
<!-- Nenhuma capacidade existente está sendo modificada em termos de requisitos de domínio. -->

## Impact

- **Código e Templates:**
  - `templates/pages/landing.html`: novo template principal da página institucional.
  - `templates/components/subdomain_check_result.html`: fragmento de resposta para o HTMX.
  - `apps/core/views.py`: view da landing page e endpoint de verificação de subdomínio.
  - `config/urls.py`: mapeamento da rota raiz `/` e da rota `/check-subdomain/`.
- **Dependências e Infraestrutura:** Não há novas dependências externas; utiliza o stack existente (Django 5.2, HTMX, Alpine.js, Tailwind v4).
- **Isolamento de Tenant:** Acesso público no host raiz sem tenant ativo no contexto (`request.tenant = None`), em conformidade com o modelo fail-closed de `docs/arquitetura.md`.
