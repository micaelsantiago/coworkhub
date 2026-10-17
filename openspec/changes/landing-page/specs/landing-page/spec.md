## Purpose

Fornece a página institucional e os pontos de contato públicos do Coworkhub no domínio raiz, permitindo que operadores de coworking compreendam o produto e iniciem o fluxo de onboarding com validação interativa de subdomínio.

## ADDED Requirements

### Requirement: Exibição da Landing Page Institucional
O sistema MUST exibir a landing page pública na raiz da aplicação quando acessada a partir do domínio institucional (`coworkhub.com.br`, `www.coworkhub.com.br` ou `localhost:8000`), sem exigir autenticação ou contexto de tenant ativo.

#### Scenario: Visitante acessa a página inicial
- **WHEN** um visitante não autenticado faz uma requisição `GET /` no domínio institucional
- **THEN** o sistema responde com status HTTP 200 contendo a landing page completa (Hero, proposta de valor, recursos do MVP, preços do plano e FAQ)

### Requirement: Validação Interativa de Subdomínio no Hero
O sistema MUST fornecer um endpoint público para validação antecipada de subdomínio via requisições assíncronas do HTMX, garantindo feedback imediato sobre formatação e disponibilidade de termos reservados.

#### Scenario: Subdomínio válido e disponível informado
- **WHEN** o usuário digita um nome como "Estação Coworking" que normaliza para `estacao-coworking`
- **THEN** o sistema retorna um fragmento indicando conformidade e disponibilidade, exibindo o endereço `estacao-coworking.coworkhub.com.br` pronto para criação

#### Scenario: Subdomínio reservado informado
- **WHEN** o usuário digita um nome que resulta em um termo reservado como `admin`, `api`, `app` ou `www`
- **THEN** o sistema recusa o subdomínio e exibe mensagem clara informando que o termo não pode ser utilizado

#### Scenario: Subdomínio com caracteres inválidos ou vazio
- **WHEN** o usuário submete um valor que não obedece ao padrão alfanumérico com hifens
- **THEN** o sistema retorna mensagem de erro de validação solicitando um nome válido

### Requirement: Acordeão de Dúvidas Frequentes (FAQ)
A landing page MUST conter um acordeão acessível com as principais dúvidas operacionais e comerciais do público-alvo, permitindo expandir e recolher respostas individualmente sem recarregar a página.

#### Scenario: Visitante interage com uma pergunta frequente
- **WHEN** o usuário clica sobre o cabeçalho de uma pergunta no FAQ
- **THEN** a resposta correspondente expande via Alpine.js e o ícone de expansão altera seu estado visual, mantendo a navegação acessível por teclado

### Requirement: Direcionamento para Onboarding e Trial
A landing page MUST apresentar chamadas para ação (CTAs) claras direcionando o visitante para o início do período de teste de 7 dias, propagando o subdomínio validado quando preenchido.

#### Scenario: Visitante aciona o botão de início do trial
- **WHEN** o usuário clica em "Começar teste grátis" após validar seu subdomínio no Hero
- **THEN** o sistema direciona o fluxo para a tela de cadastro inicial com os dados antecipados
