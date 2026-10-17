## 1. Backend e Validação de Subdomínio

- [ ] 1.1 Implementar normalização de slug e validação de termos reservados (`RESERVED_SUBDOMAINS`) em `apps/core/services.py` ou `apps/tenants/services.py` e verificar com testes unitários.
- [ ] 1.2 Criar endpoint `POST /check-subdomain/` e view da landing page em `apps/core/views.py` e mapear em `config/urls.py`, verificando resposta HTTP 200 via teste.
- [ ] 1.3 Criar template parcial `templates/components/subdomain_check_result.html` para renderização das mensagens de sucesso e erro do HTMX.

## 2. Interface da Landing Page

- [ ] 2.1 Criar template `templates/pages/landing.html` estruturando Navbar, Hero com checker de subdomínio e mock visual de reservas.
- [ ] 2.2 Adicionar seções de Contraste Operacional, Pilares do MVP, Onboarding em 3 passos, Preço/Trial transparente e Footer institucional.
- [ ] 2.3 Implementar componente de FAQ em acordeão acessível utilizando Alpine.js (`x-data`, `@click`, `x-collapse`) e verificar interação no navegador/DOM.
- [ ] 2.4 Atualizar `config/urls.py` para apontar a rota raiz `/` para a nova landing page.

## 3. Testes Automatizados e Verificação Final

- [ ] 3.1 Criar testes em `tests/test_landing_page.py` cobrindo requisição da landing page e os cenários de validação de subdomínio (válido, reservado, inválido e vazio).
- [ ] 3.2 Executar `make lint` e corrigir eventuais advertências de formatação ou linting.
- [ ] 3.3 Executar `make test` e verificar que toda a suíte de testes passa com sucesso.
