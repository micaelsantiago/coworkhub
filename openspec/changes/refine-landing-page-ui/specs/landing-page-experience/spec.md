## Purpose

Define uma experiência pública clara, confiável e eficiente para apresentar o Coworkhub e conduzir operadores de coworking ao início do cadastro em qualquer tamanho de tela.

## ADDED Requirements

### Requirement: Narrativa direta e verificável
A landing page MUST apresentar uma sequência de conteúdo que priorize a proposta de valor, uma demonstração reconhecível do produto, os benefícios operacionais, o funcionamento, a oferta e as dúvidas necessárias para a decisão. Alegações sobre disponibilidade, prazo, preço, segurança ou resultado MUST ser sustentadas pela implementação ou pela documentação vigente; funcionalidades ainda planejadas MUST ser identificadas como parte do MVP ou removidas da promessa comercial.

#### Scenario: Visitante percorre a página
- **WHEN** um visitante acessa a landing page pública
- **THEN** ele encontra uma proposta de valor e uma ação principal antes das seções de detalhamento
- **AND** cada seção posterior acrescenta uma informação distinta, sem repetir a mesma lista de benefícios em cartões equivalentes

#### Scenario: Conteúdo descreve capacidade planejada
- **WHEN** a página menciona uma capacidade documentada que ainda não está implementada
- **THEN** o texto não a apresenta como comportamento atualmente disponível

### Requirement: Linguagem visual consistente com o Coworkhub
A landing page MUST preservar a paleta principal existente do projeto e usar hierarquia tipográfica, contraste, divisores, superfícies e demonstrações do fluxo operacional para comunicar estabilidade, segurança e modernidade. Elementos decorativos MUST apoiar a compreensão ou a hierarquia e não podem depender de gradientes genéricos, excesso de sombras ou uma grade uniforme de cartões para preencher espaço.

#### Scenario: Identidade visual da página refinada
- **WHEN** a landing page é comparada aos tokens visuais do projeto
- **THEN** o terracota primário, preto, branco e neutros existentes continuam reconhecíveis
- **AND** a demonstração operacional do produto funciona como o principal elemento visual da composição

### Requirement: Experiência mobile-first
A landing page MUST oferecer a mesma informação e ações essenciais a partir de 320 px de largura, sem rolagem horizontal, sobreposição ou texto truncado que impeça compreensão. A ordem visual no mobile MUST priorizar mensagem, ação principal, validação de subdomínio e demonstração do produto antes de conteúdo secundário.

#### Scenario: Acesso em viewport móvel estreita
- **WHEN** a página é exibida em uma viewport de 320 px de largura
- **THEN** o visitante consegue ler o conteúdo, operar a navegação, preencher o subdomínio, acionar o CTA e usar o FAQ sem zoom ou rolagem horizontal
- **AND** os controles interativos possuem área mínima de toque de 44 por 44 CSS pixels

#### Scenario: Ampliação progressiva em desktop
- **WHEN** a viewport dispõe de espaço suficiente para múltiplas colunas
- **THEN** a composição amplia e redistribui o conteúdo sem alterar sua ordem semântica nem esconder ações disponíveis no mobile

### Requirement: Acessibilidade e aprimoramento progressivo
A landing page MUST usar estrutura semântica, foco de teclado visível, contraste legível e nomes acessíveis para seus controles. O conteúdo, a proposta de valor e os links MUST permanecer disponíveis quando animações ou JavaScript não executarem; interações dinâmicas existentes MUST comunicar mudanças a tecnologias assistivas.

#### Scenario: Navegação por teclado
- **WHEN** o visitante percorre os controles usando apenas teclado
- **THEN** cada elemento interativo recebe um indicador de foco visível e segue uma ordem coerente com a leitura da página

#### Scenario: JavaScript indisponível
- **WHEN** o JavaScript não carrega ou falha durante a visita
- **THEN** todo conteúdo comercial e todos os links convencionais continuam visíveis e utilizáveis
- **AND** o formulário mantém uma submissão HTTP funcional para a validação de subdomínio

### Requirement: Movimento contido e adaptável
Movimentos automáticos MUST ser limitados a uma única sequência breve no hero, animar apenas transformações e opacidade e nunca bloquear leitura ou interação. A página MUST desativar animações não essenciais quando o visitante preferir movimento reduzido.

#### Scenario: Preferência por movimento reduzido
- **WHEN** o dispositivo informa `prefers-reduced-motion: reduce`
- **THEN** o conteúdo é apresentado imediatamente em seu estado final, sem deslocamentos ou transições automáticas não essenciais

#### Scenario: Carregamento normal do hero
- **WHEN** o visitante não solicita redução de movimento
- **THEN** qualquer entrada automática termina rapidamente, não causa mudança de layout e não se repete durante a rolagem

### Requirement: Orçamento de desempenho da página pública
A landing page MUST evitar dependências de animação e recursos visuais pesados, reservar espaço para toda mídia dimensionável e carregar recursos não críticos sem bloquear a primeira renderização. Em uma auditoria Lighthouse mobile de produção, executada com o perfil padrão, a página MUST atingir pontuação de desempenho de pelo menos 90, pontuação de acessibilidade de pelo menos 95, Largest Contentful Paint de até 2,5 segundos e Cumulative Layout Shift de até 0,1.

#### Scenario: Auditoria móvel da landing page
- **WHEN** a versão de produção é auditada no perfil mobile padrão do Lighthouse após uma carga fria
- **THEN** os limites definidos de desempenho, acessibilidade, LCP e CLS são atendidos

#### Scenario: Recursos visuais são carregados
- **WHEN** logotipos, ícones ou demonstrações visuais entram na página
- **THEN** suas dimensões ou proporções são reservadas antes do carregamento
- **AND** nenhum recurso remoto de terceiros é necessário apenas para decoração ou movimento

### Requirement: Preservação dos fluxos públicos existentes
O refinamento MUST preservar a rota pública da landing page, a validação de subdomínio por HTMX, a submissão HTTP equivalente, o FAQ interativo e os destinos atuais dos CTAs, sem introduzir leitura ou gravação de dados pertencentes a tenant.

#### Scenario: Visitante valida um subdomínio
- **WHEN** o visitante informa um nome no formulário principal
- **THEN** recebe o mesmo feedback autoritativo do backend para valores válidos e inválidos, independentemente do novo layout

#### Scenario: Visitante usa um CTA secundário
- **WHEN** o visitante aciona um CTA secundário da página
- **THEN** ele é conduzido à mesma ação principal sem perder acesso ao conteúdo ou ao formulário
