## Why

A landing page atual já comunica o produto e oferece validação de subdomínio, mas sua composição repete padrões genéricos de SaaS — blocos centralizados, muitos cartões equivalentes e pouca hierarquia visual — e não estabelece com clareza a sensação de estabilidade, segurança e modernidade desejada para o Coworkhub. O refinamento deve tornar a experiência mais direta e mobile-first sem aumentar o custo de carregamento ou apresentar capacidades planejadas como se já estivessem disponíveis.

## What Changes

- Reorganizar a narrativa da landing page para uma leitura mais curta e progressiva: proposta de valor, demonstração operacional, benefícios verificáveis, funcionamento, oferta e dúvidas.
- Definir uma direção visual minimalista, porém substancial, baseada na paleta existente (`#b85c38`, preto, branco e superfícies neutras), usando ritmo tipográfico, divisores, contraste e uma demonstração do produto como principal elemento memorável em vez de decoração genérica.
- Projetar primeiro para telas móveis, com conteúdo e CTA prioritários acima da dobra, navegação compacta, alvos de toque adequados e ausência de overflow horizontal; ampliar a composição de forma progressiva em telas maiores.
- Reduzir repetição de cartões, textos longos, jargão técnico voltado à arquitetura e alegações não sustentadas pela implementação atual; preservar apenas informações de produto respaldadas pela documentação e distinguir disponibilidade atual de direção do MVP quando necessário.
- Estabelecer um orçamento de desempenho para a experiência pública, incluindo CSS/JavaScript enxutos, estabilidade de layout, carregamento não bloqueante e mídia otimizada.
- Adotar movimento de maneira contida, limitado a uma sequência curta no hero e realizável com CSS. As skills de GSAP orientam os critérios de composição, acessibilidade e desempenho, mas GSAP Core, Timeline, ScrollTrigger e plugins não serão adicionados nesta iteração porque a interação proposta não exige controle de timeline ou scroll. A experiência deve permanecer completa sem JavaScript e respeitar `prefers-reduced-motion`.
- Preservar a validação HTMX de subdomínio, o FAQ em Alpine.js, os destinos de CTA e a arquitetura Django server-rendered existentes.

## Capabilities

### New Capabilities

- `landing-page-experience`: Experiência pública refinada da landing page, cobrindo hierarquia de conteúdo, apresentação visual, responsividade mobile-first, acessibilidade, movimento progressivo e desempenho percebido.

### Modified Capabilities

<!-- Nenhuma capability principal sincronizada existe atualmente para modificação. A mudança `landing-page` permanece separada e não será sincronizada ou arquivada por este trabalho. -->

## Impact

- **Templates e estilos:** `templates/pages/landing.html`, possivelmente `templates/base.html`, componentes públicos reutilizados e `assets/css/input.css`.
- **JavaScript e dependências:** não adicionar GSAP nem outra dependência de animação; manter `assets/js/app.js` limitado às integrações existentes de Alpine.js e HTMX.
- **Testes:** testes de renderização existentes permanecem válidos e deverão ser complementados com verificações estruturais, acessíveis e responsivas apropriadas ao stack atual.
- **Backend e domínio:** não há mudança em regras de negócio, endpoints, persistência, modelos ou migrations. A página continua pública e não lê nem grava dados de tenant, portanto não altera o isolamento multi-tenant.
- **Compatibilidade:** não há mudança intencional nas URLs públicas, no contrato HTMX do verificador de subdomínio ou no comportamento do FAQ.
