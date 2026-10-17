## 1. Linha de base e conteúdo

- [x] 1.1 Registrar screenshots da landing atual em 320, 375, 768, 1024 e 1440 px e uma auditoria Lighthouse mobile de produção, verificando que os arquivos e resultados permitem comparação antes/depois.
- [x] 1.2 Inventariar cada afirmação e CTA do template atual contra implementação, `docs/mvp.md` e `docs/dominio.md`; definir o que permanece, o que será identificado como escopo do MVP e o que será removido, verificando que nenhuma alegação final depende de estatística, cliente, certificação ou capacidade não sustentada.
- [x] 1.3 Consolidar a copy em uma narrativa de proposta, demonstração, benefícios, processo, oferta e FAQ, verificando por revisão que cada seção comunica uma única ideia, usa linguagem do operador de coworking e mantém a ação principal consistente.

## 2. Estrutura e direção visual

- [x] 2.1 Refatorar `templates/pages/landing.html` na ordem semântica mobile-first definida em `design.md`, preservando rota, formulário, nomes de campos, atributos HTMX, destinos de CTA e comportamento Alpine; verificar com os testes focados da landing page.
- [x] 2.2 Aplicar a direção “painel operacional calmo” com os tokens existentes, hierarquia predominantemente à esquerda, divisores e superfícies contidas, verificando visualmente que o mock operacional é o único foco gráfico dominante e que não há grade repetitiva de cartões, gradientes ou sombras decorativas excessivas.
- [x] 2.3 Adaptar o mock operacional para conteúdo fluido e realista, removendo data fixa e jargão interno, verificando em 320 px que estados, horários e ação principal permanecem legíveis sem `scale()` ou overflow horizontal.
- [x] 2.4 Implementar header e navegação compactos no mobile e progressivos no desktop, verificando acesso por teclado, CTA disponível, alvos de toque de 44 px e âncoras não ocultas pelo header fixo.

## 3. Acessibilidade e movimento

- [x] 3.1 Adicionar link de salto, landmarks, heading hierarchy, foco visível, nomes acessíveis, `aria-controls`/estado do FAQ e tratamento correto de ícones decorativos, verificando a página por teclado e com a auditoria de acessibilidade do Lighthouse.
- [x] 3.2 Implementar no máximo uma entrada CSS breve no hero usando apenas `transform` e `opacity`, com conteúdo visível por padrão e override de `prefers-reduced-motion`, verificando que não há animação por rolagem, dependência de JavaScript, mudança de layout ou pacote GSAP instalado.
- [x] 3.3 Validar a página com JavaScript desabilitado, verificando que conteúdo e links permanecem disponíveis e que a submissão HTTP do formulário continua retornando feedback do backend.

## 4. Desempenho e responsividade

- [x] 4.1 Dimensionar SVGs e demais mídias, evitar recursos remotos e revisar o cache-busting dos assets sem introduzir cache obsoleto, verificando no painel de rede que não há recurso decorativo de terceiro nem mudança de layout causada por mídia.
- [x] 4.2 Gerar os assets minificados com o comando de build frontend do projeto e comparar tamanhos com a linha de base, verificando que não foi adicionada dependência de animação e que CSS/JavaScript não apresentam regressão injustificada.
- [x] 4.3 Revisar 320, 375, 768, 1024 e 1440 px, verificando ausência de overflow horizontal, sobreposição ou truncamento impeditivo e registrando screenshots finais para comparação.
- [x] 4.4 Executar Lighthouse mobile em build de produção com carga fria e perfil padrão, verificando desempenho ≥ 90, acessibilidade ≥ 95, LCP ≤ 2,5 s e CLS ≤ 0,1; documentar ambiente e resultado no relatório da execução.

## 5. Testes e revisão final

- [x] 5.1 Atualizar `tests/test_landing_page.py` para validar a nova estrutura estável sem acoplar o teste a copy decorativa, preservando cobertura da renderização, do formulário e dos estados válido/inválido do fragmento HTMX; verificar com o teste focado da landing page.
- [x] 5.2 Aplicar a revisão atualizada de `web-design-guidelines` ao template, estilos e interações alterados e corrigir achados de acessibilidade/UX, verificando que não restam achados de severidade alta.
- [x] 5.3 Executar `make lint` e corrigir todos os erros.
- [x] 5.4 Executar `make test` e confirmar que toda a suíte passa.
- [x] 5.5 Revisar o diff final e deixar todas as alterações locais, sem commit, verificando que apenas arquivos necessários ao refinamento foram modificados e reportando ao usuário como iniciar e validar a interface.
