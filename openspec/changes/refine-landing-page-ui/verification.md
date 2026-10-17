## Ambiente

- Data: 17 de outubro de 2026
- URL local: `http://127.0.0.1:58000/`
- Navegador: Google Chrome headless instalado no ambiente
- Assets: build minificado com `docker compose run --rm frontend sh -c "npm ci && npm run build"`
- Lighthouse: `12.8.2`, perfil mobile padrão, carga fria, categorias `performance` e `accessibility`

## Linha de base

Capturas registradas em 320, 375, 768, 1024 e 1440 px antes da alteração, em `/tmp/opencode/coworkhub-landing/baseline/`.

| Métrica | Resultado |
|---|---:|
| Performance | 92 |
| Acessibilidade | 93 |
| LCP | 3.392 ms |
| CLS | 0 |

## Resultado final

Capturas registradas nas mesmas larguras em `/tmp/opencode/coworkhub-landing/final/`. A revisão visual confirmou a ordem mobile-first e resultou no ajuste da grade do mock para não recortar a última coluna em 320 px.

| Métrica | Resultado | Limite da spec |
|---|---:|---:|
| Performance | 98 | ≥ 90 |
| Acessibilidade | 100 | ≥ 95 |
| LCP | 2.323 ms | ≤ 2.500 ms |
| CLS | 0 | ≤ 0,1 |

O build final gerou 42.009 bytes de CSS e 145.142 bytes de JavaScript. Não há dependência ou uso de GSAP. A submissão HTTP sem HTMX foi validada com cookie e token CSRF reais e retornou HTTP 200 com o subdomínio normalizado.

## Verificações automatizadas

- `docker compose run --rm web pytest tests/test_landing_page.py`: 12 testes aprovados.
- `make lint`: aprovado.
- `make test`: 15 testes aprovados.
- `openspec validate refine-landing-page-ui --strict`: aprovado.
