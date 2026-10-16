# Coworkhub: Infraestrutura

> Documento de infraestrutura e operação. A arquitetura de software está em `arquitetura.md`.
> O escopo que esta infraestrutura precisa atender está definido em `mvp.md`.

## 1. Visão geral

```
Usuário → Cloudflare (DNS, proxy, WAF, Turnstile, cache) → Tunnel ou Caddy → VPS Contabo
                                                                              ├─ Django (gunicorn)
                                                                              ├─ Celery worker + beat
                                                                              ├─ PostgreSQL
                                                                              └─ Redis

Uploads  → Cloudflare R2
Backups  → Cloudflare R2 (restic / pgBackRest)
Erros    → Sentry
E-mail   → provedor transacional (Resend, Postmark ou Amazon SES)
Cobrança → Asaas (API REST, Sandbox para dev/testes, webhooks com token)
```

## 2. Hospedagem

**Contabo, plano Cloud VPS 10 SSD:**

| Recurso | Valor |
|---|---|
| vCPUs | 4 |
| RAM | 8 GB |
| Disco | 150 GB SSD |
| Rede | 200 Mbit/s |
| Snapshots | 1 |

**Limitação importante:** é um ponto único de falha, e o único snapshot fica na mesma infraestrutura, portanto **não substitui backup**. Para o MVP isso é aceitável, desde que existam backups externos e um runbook de reconstrução (seção 7).

## 3. Cloudflare

O domínio já está registrado e com DNS na Cloudflare.

### 3.1 DNS e subdomínios

- Registro wildcard `*.seudominio.com.br` apontando para a VPS, com proxy ligado (nuvem laranja). Cada tenant em `tenant.seudominio.com.br` funciona sem criar DNS por cliente.
- O certificado universal gratuito cobre **um nível** de wildcard (`acme.dominio`), o suficiente para este projeto.
- Subdomínios reservados, que não podem ser usados por tenants: `www`, `app`, `admin`, `api`, `status`, `mail`.

### 3.2 TLS

- Modo de criptografia: **Full (strict)**. Nunca usar "Flexible".
- Certificado de origem no proxy da VPS, por uma destas opções:
  1. **Cloudflare Origin Certificate** wildcard instalado no Caddy (mais simples, validade de até 15 anos).
  2. Caddy emitindo Let's Encrypt via **DNS-01** com o plugin `caddy-dns/cloudflare` (requer token de API).

### 3.3 Proteção da origem

- **Opção A:** firewall da VPS libera 80/443 somente para os IPs da Cloudflare.
- **Opção B (preferida):** **Cloudflare Tunnel** (`cloudflared` em container). A VPS não expõe nenhuma porta web.
- No Django: ler o IP real via header `CF-Connecting-IP`, configurar `SECURE_PROXY_SSL_HEADER` e `CSRF_TRUSTED_ORIGINS` com wildcard de subdomínio.

### 3.4 Segurança e performance

- **WAF e rate limiting** nas rotas de login, cadastro e reset de senha.
- **Turnstile** (CAPTCHA gratuito) em cadastro e login.
- Cache de estáticos (CSS, JS, imagens). **Não fazer cache de HTML autenticado.**
- **R2** (compatível com S3, sem taxa de saída) para uploads (logos, fotos de espaços), em vez do disco da VPS.

### 3.5 Evolução

- Domínio próprio por cliente (`reservas.cowork-do-cliente.com`): usar **Cloudflare for SaaS (Custom Hostnames)**. O model `Domain` da aplicação já prevê isso.

## 4. Serviços na VPS (Docker Compose)

| Serviço | Função | `mem_reservation` | `mem_limit` |
|---|---|---|---|
| `postgres` | PostgreSQL 16 | 1.0 GB | 2.0 GB |
| `redis` | Redis (cache e broker) | 128 MB | 512 MB |
| `web` | Django + Gunicorn (3 workers) | 512 MB | 1.5 GB |
| `worker` | Celery worker (`--concurrency=2`) | 256 MB | 1.0 GB |
| `beat` | Celery beat | 64 MB | 256 MB |
| `cloudflared` | Cloudflare Tunnel (ou Caddy) | 64 MB | 256 MB |
| **Total alocado** | | **~2.0 GB** | **~5.5 GB** |

> **Margem de segurança:** A soma dos limites máximos (~5.5 GB) deixa cerca de 2.5 GB livres na VPS de 8 GB para o kernel Linux, Docker daemon e buffer de páginas, prevenindo que um processo cause o acionamento do OOM Killer no PostgreSQL.

### Boas práticas e mitigação de SPOF/OOM

1. **Configuração de Swap de 2 GB:** Criar arquivo de swap de 2 GB (`/swapfile`) com `vm.swappiness=10`. Isso serve como colchão amortecedor para absorver picos transitórios de memória sem derrubar containers.
2. **Prevenção de Vazamento no Celery:** Rodar workers com `--max-tasks-per-child=100` e concorrência limitada (`--concurrency=2`). A cada 100 tarefas, o processo filho do Celery é reciclado, evitando consumo progressivo de RAM.
3. **Isolamento de Rede:** Postgres e Redis escutam exclusivamente na rede interna do Docker Compose, sem bind de portas no host (`ports:` omitido, usando apenas `expose:`).
4. **Rotação de Logs do Docker:** Configurar no `daemon.json` ou por container `log-driver: json-file` com `max-size: "20m"` e `max-file: "5"`.
5. **Monitoramento de Disco:** Alertas via Uptime Kuma / Healthchecks quando uso de disco ultrapassar 80%.

## 5. Banco de dados

- **PostgreSQL** com tuning para a fatia alocada: `shared_buffers = 512MB`, `effective_cache_size = 1.5GB`, `work_mem = 16MB`, `maintenance_work_mem = 128MB`.
- Extensão `btree_gist` habilitada para suporte a constraints de exclusão (`ExclusionConstraint`) de sobreposição temporal.
- Row-Level Security ativado como camada de defesa em profundidade (ver `arquitetura.md`).

## 6. Segurança do servidor

- Acesso SSH somente por chave (desabilitar senha e login de root via `/etc/ssh/sshd_config`).
- Firewall (UFW) bloqueando conexões externas nas portas do banco e Redis.
- `fail2ban` ativo no SSH e atualizações automáticas de segurança do SO (`unattended-upgrades`).
- Segredos fora do repositório (arquivo `.env` com permissão restrita `600` e backup seguro em cofre de senhas).
- Tokens de API da Cloudflare com escopo mínimo (apenas permissão de túnel e DNS necessário).

## 7. Backup, resiliência e recuperação de desastres

Como a VPS única é um ponto único de falha de hardware, a recuperação depende de um processo de backup e restauração automatizado e testado:

### 7.1 Estratégia de Backup Offsite (Cloudflare R2)

- **Ferramenta:** `pg_dump` horário/diário compactado e criptografado com `restic` (ou `pgBackRest`), enviado diretamente para bucket privado no **Cloudflare R2** (fora da infraestrutura da Contabo).
- **Retenção:** 7 backups diários, 4 semanais e 3 mensais.
- **Mídia/Uploads:** Imagens e logos enviados por tenants são gravados diretamente no R2 (S3-compatible) ou sincronizados continuamente, sem depender do disco local da VPS.

### 7.2 Metas de Recuperação (RPO e RTO)

| Métrica | Meta MVP | Estratégia |
|---|---|---|
| **RPO (Ponto de Recuperação)** | **<= 1 hora** | Dumps horários incrementais (ou WAL archiving) no R2 |
| **RTO (Tempo de Recuperação)** | **<= 2 horas** | Subida de nova VPS via Docker Compose + restauração do último snapshot do R2 |

### 7.3 Monitoramento com Deadman Switch

- O script de backup dispara um sinal HTTP via curl para o **Healthchecks.io** ao concluir com sucesso.
- Se o Healthchecks.io não receber o sinal dentro da janela esperada (ex: a cada 60 minutos + 15 min de tolerância), emite alerta imediato via Telegram e e-mail para os mantenedores.
- **Runbook de Reconstrução:** Manter script `scripts/restore.sh` versionado para restaurar banco e arquivos a partir de qualquer máquina limpa com Docker instalado. Teste de restauração semestral obrigatório.

## 8. E-mail transacional

- Provedor transacional dedicado (Resend, Postmark ou Amazon SES). IPs de VPS Contabo são expressamente proibidos para envio de e-mails para evitar problemas de entregabilidade e reputação.
- DNS configurado na Cloudflare com **SPF, DKIM e DMARC** rígidos (registros DNS de e-mail com nuvem cinza / sem proxy).

## 9. Observabilidade

Mapeamento mínimo enxuto para o MVP:

- **Sentry:** Captura de exceções e erros 500 no Django e falhas de tasks no Celery.
- **Logs Estruturados:** Formato JSON no stdout com inclusão de `request_id`, `tenant_id` e `user_id`.
- **Healthchecks.io:** Deadman switch para cron de backups e tarefas agendadas do Celery Beat.
- **Endpoints de Saúde:**
  - `/healthz`: Retorna 200 se o processo Django estiver respondendo.
  - `/readyz`: Valida conectividade com PostgreSQL e Redis antes de rotear tráfego.

## 10. Ambientes e pipeline de deploy

### 10.1 Ambientes

1. **Desenvolvimento Local:** Docker Compose com Postgres e Redis locais, Django em modo de debug e Celery worker.
2. **Produção:** VPS Contabo com Cloudflare Tunnel.

### 10.2 CI/CD e Deploy com Downtime Mínimo

- **GitHub Actions:**
  1. Executa lint e testes automatizados (`pytest`, incluindo a suite `TenantIsolationTestCase`).
  2. Constrói imagem Docker e publica em registro de containers (ex: GitHub Container Registry).
- **Fluxo de Deploy na VPS:**
  1. Download da nova imagem Docker (`docker compose pull`).
  2. Execução de migrações (`docker compose run --rm web python manage.py migrate`).
  3. Reload gracioso do Gunicorn (`kill -HUP <pid>` ou reinicialização controlada do contêiner `web`).
  4. Reinicialização dos workers Celery (`docker compose restart worker beat`).
- **Padrão Expand/Contract em Migrações:**
  - Migrações devem ser sempre compatíveis com a versão anterior do código.
  - Nunca remover ou renomear colunas na mesma release em que a aplicação muda. Adiciona nova coluna (nullable) -> deploy do código novo -> preenche dados -> remove coluna antiga na release seguinte.

## 11. Pontos em aberto

- Provedor de e-mail transacional inicial a contratar (Resend vs Postmark).
- Plano de transição para banco gerenciado (ex: Neon ou Supabase) caso o volume de tenants justifique eliminar o Postgres local da VPS.
