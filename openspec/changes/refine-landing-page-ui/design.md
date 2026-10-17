## Context

Veja `proposal.md` para a motivação. A landing atual é um template Django único com aproximadamente 700 linhas, construído com Tailwind CSS v4. Ela já contém header fixo, hero, formulário HTMX, mock de agenda, seções comerciais, preço, FAQ em Alpine.js e CTA final. Os testes cobrem renderização e o serviço/fragmento de validação de subdomínio, mas não cobrem responsividade, acessibilidade ou desempenho.

O frontend é compilado em um único CSS e um único bundle JavaScript. O bundle atual contém Alpine.js, seus plugins e HTMX; não há biblioteca de animação instalada. A mudança não envolve modelos, banco, rotas ou regras de domínio.

## Goals / Non-Goals

**Goals:**
- Tornar a hierarquia e a direção visual específicas ao contexto de operação de coworkings, reduzindo a aparência de template SaaS.
- Entregar uma composição funcional desde 320 px e expandi-la progressivamente para desktop.
- Melhorar credibilidade por meio de linguagem direta, densidade controlada e demonstração concreta do fluxo de reservas.
- Manter a página rápida, estável, acessível e funcional sem JavaScript para o conteúdo principal.

**Non-Goals:**
- Redesenhar o onboarding, o endpoint de validação, a regra de subdomínio ou o FAQ como componente global.
- Criar SPA, API, captura de analytics, depoimentos, logos de clientes ou métricas sem evidência.
- Adicionar fontes remotas, vídeos, imagens hero pesadas, GSAP, smooth scrolling, parallax, pinning ou animações vinculadas à rolagem.
- Alterar modelos ou banco de dados; não há migration nem constraint nova.

## Decisions

### 1. Direção visual: “painel operacional calmo”

A página usará estrutura inspirada em uma grade de operação: alinhamento predominantemente à esquerda, divisores finos, blocos de dados compactos, espaços regulares e um único mock detalhado da agenda. Isso comunica ordem e previsibilidade sem recorrer à grade repetitiva de cards.

Tokens preservados e explicitamente reutilizados:

| Papel | Token |
|---|---|
| Ação e destaque | `#B85C38` |
| Hover | `#A24F2E` |
| Texto principal | `#000000` |
| Superfície principal | `#FFFFFF` |
| Superfície secundária | `#F9FAFB` |
| Linhas e limites | `#E5E7EB` |

A tipografia continuará no stack de sistema para evitar download adicional e manter renderização imediata. A personalidade virá de escala, largura de linha, peso, alinhamento e uso de numerais tabulares no mock, não da introdução de uma fonte de marca ainda inexistente.

Alternativa descartada: gradientes, glassmorphism e sombras extensas. Esses recursos enfraquecem o pedido de estabilidade e aumentam pintura sem comunicar o domínio.

### 2. Arquitetura de conteúdo reduzida

A estrutura será condensada para evitar oito faixas visualmente equivalentes:

```text
MOBILE (ordem semântica)
┌──────────────────────────┐
│ marca              CTA  │
├──────────────────────────┤
│ proposta de valor        │
│ texto curto              │
│ [subdomínio] [continuar] │
│ sinais de confiança      │
├──────────────────────────┤
│ mock operacional         │
├──────────────────────────┤
│ problema → benefício     │
├──────────────────────────┤
│ 3 passos reais           │
├──────────────────────────┤
│ oferta + condições       │
├──────────────────────────┤
│ FAQ                      │
├──────────────────────────┤
│ CTA final + rodapé       │
└──────────────────────────┘

DESKTOP
┌────────────────────────────────────────────┐
│ marca       navegação curta          CTA  │
├──────────────────────┬─────────────────────┤
│ proposta + formulário│ mock operacional    │
├──────────────────────┴─────────────────────┤
│ argumento em faixas assimétricas           │
├──────────────────────────┬─────────────────┤
│ processo                 │ oferta          │
├──────────────────────────┴─────────────────┤
│ FAQ + CTA final                             │
└────────────────────────────────────────────┘
```

O comparativo e os recursos atuais serão reconciliados em uma seção de argumento com uma ideia por bloco. O processo mantém numeração porque é de fato sequencial. Preço e trial só permanecem com afirmações que a documentação vigente sustenta; capacidades ainda não implementadas serão formuladas como escopo do MVP, não como prova atual.

Alternativa descartada: manter todas as seções e apenas trocar cores/raios. Isso preservaria o problema de hierarquia e repetição identificado na proposta.

### 3. Mobile-first como base, não adaptação

As classes-base representarão o layout de 320–767 px. Breakpoints serão usados apenas para ampliar espaçamento, habilitar navegação completa e formar colunas. O mock da agenda terá uma versão intrinsecamente fluida: textos auxiliares podem quebrar linha, grades internas não dependerão de largura fixa e detalhes não essenciais podem ser simplificados sem esconder a ação ou o estado principal.

Header, formulário e FAQ terão controles com pelo menos 44 px em ambos os eixos. Links âncora considerarão o header fixo por meio de margem de rolagem. A ordem do DOM seguirá a ordem móvel e semântica; CSS não inverterá conteúdo essencial no desktop.

Alternativa descartada: desenhar a composição desktop e empilhar colunas no final. O template atual já apresenta trechos densos e labels que ficam frágeis em larguras estreitas.

### 4. Movimento sem GSAP nesta iteração

As skills adicionadas foram avaliadas:

- **gsap-core:** adequado para tweens responsivos e `prefers-reduced-motion`, mas desnecessário para uma única entrada curta.
- **gsap-timeline:** útil para coreografias coordenadas; o hero proposto não precisa de controle de reprodução, labels ou múltiplas fases.
- **gsap-performance:** suas recomendações serão adotadas: somente `transform`/`opacity`, nada de propriedades que causem layout, e `will-change` apenas durante a animação.
- **gsap-scrolltrigger:** inadequado para este objetivo; animações por rolagem, scrub e pinning aumentariam trabalho em dispositivos móveis e competiriam com a leitura direta.
- **gsap-plugins:** Flip, SplitText, ScrollSmoother e demais plugins não resolvem uma necessidade desta interface.

Portanto, não será adicionada a dependência `gsap`. Uma única animação CSS opcional poderá coordenar título, texto/CTA e mock com atrasos curtos. O estado inicial do HTML sempre será visível; uma media query para `prefers-reduced-motion: reduce` removerá deslocamentos e durações. Não haverá reveal por seção durante a rolagem.

Alternativa descartada: instalar GSAP apenas para demonstrar as novas skills. Isso acrescentaria bytes e complexidade sem necessidade funcional. Se uma mudança futura exigir timeline interrompível, scroll-driven ou morphing, a decisão deve ser reavaliada usando `gsap-core`, `gsap-timeline` e `gsap-performance`.

### 5. Desempenho e estabilidade como critérios de aceite

O redesign usará SVGs locais já existentes, ícones inline e CSS. Toda mídia terá `width`/`height` ou `aspect-ratio`; não serão adicionados scripts remotos, fontes externas, vídeo ou imagens raster grandes. O CSS gerado e o bundle continuarão minificados pelo pipeline atual. O cache-busting por timestamp em `base.html` deve ser revisto durante a implementação, pois muda a URL a cada renderização e reduz o reaproveitamento de cache; qualquer ajuste deve preservar atualização confiável dos assets.

A validação combinará inspeção em 320, 375, 768, 1024 e 1440 px com Lighthouse mobile em build de produção. A auditoria deve registrar ambiente e resultados para que os números do spec sejam reproduzíveis.

Alternativa descartada: lazy-load indiscriminado de conteúdo acima da dobra. O hero e o mock principal devem renderizar sem atraso; apenas mídia realmente abaixo da dobra pode ser adiada.

### 6. Acessibilidade e conteúdo confiável

O template manterá landmarks e heading hierarchy, adicionará link de salto para o conteúdo, foco claramente visível, `aria-controls` no FAQ e feedback anunciado no formulário. Ícones decorativos serão ignorados por tecnologia assistiva. O texto deixará de expor detalhes internos como “fail-closed” e “motor de concorrência no banco” como argumento principal; esses mecanismos podem ser traduzidos em benefícios verificáveis sem alegar certificações ou garantias inexistentes.

O agente de implementação indicado é o `agente-frontend`. As skills adequadas para a próxima fase são `frontend-design` para direção visual, `copywriting` para clareza e suporte das alegações, `web-design-guidelines` para a revisão final e os princípios de `gsap-performance` para auditar qualquer movimento CSS. As skills `gsap-core`, `gsap-timeline`, `gsap-scrolltrigger` e `gsap-plugins` não devem ser aplicadas como dependências nesta mudança.

## Risks / Trade-offs

- **[Risco] Reduzir seções pode remover informação necessária à decisão** → Mapear cada afirmação atual para a nova narrativa antes de excluir e preservar respostas úteis no FAQ.
- **[Risco] O mock operacional ainda pode ficar denso em 320 px** → Projetar primeiro sua versão móvel e testar conteúdo real, sem depender apenas de `scale()`.
- **[Risco] Metas Lighthouse variarem entre execuções** → Usar build de produção, carga fria e perfil padrão documentado; corrigir regressões consistentes, não ruído isolado.
- **[Risco] CSS de entrada causar flash ou conteúdo invisível** → HTML visível por padrão; animação somente como aprimoramento e nunca por classe que dependa de JavaScript para revelar conteúdo.
- **[Trade-off] Stack de sistema é menos distintivo que uma fonte própria** → Priorizar desempenho e consistência agora; uma futura definição formal de marca pode introduzir fonte local otimizada.
- **[Trade-off] Não usar GSAP reduz possibilidades de coreografia** → A restrição protege o orçamento e combina com o princípio de uma experiência calma e direta.

## Migration Plan

1. Capturar a linha de base visual e Lighthouse da landing atual.
2. Refatorar conteúdo e layout mantendo URLs, nomes de campos e alvos HTMX existentes.
3. Aplicar tokens e movimento CSS progressivo; validar sem JavaScript e com movimento reduzido.
4. Gerar assets de produção e executar validações responsivas, acessíveis e de desempenho.
5. Em caso de regressão, reverter os arquivos de template/estilo alterados; não há dados, migrations ou processo de rollback de banco.
