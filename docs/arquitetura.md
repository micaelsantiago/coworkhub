# Coworkhub: Arquitetura da Aplicação

> Plataforma SaaS multi-tenant para empresas de coworking.
> Este documento descreve as decisões de arquitetura de software. A infraestrutura está em `infraestrutura.md`.
> O contexto de produto e as regras funcionais estão em `produto.md`, `mvp.md` e `dominio.md`.

## 1. Visão geral

O Coworkhub é um SaaS em que cada empresa de coworking é um **tenant**, com seus próprios espaços, membros, planos operacionais e reservas, isolados dos demais.

A aplicação é um **monolito Django fullstack**: o servidor renderiza as páginas e a interatividade vem de HTMX e Alpine.js, sem SPA e sem API separada na primeira fase.

## 2. Decisões tomadas

| Tema | Decisão | Observação |
|---|---|---|
| Framework | **Django** (fullstack) | Auth, ORM, migrations, admin e permissões já prontos |
| Frontend | Templates Django + **HTMX** + **Alpine.js** + **Tailwind CSS** | Sem frontend separado nesta fase |
| Banco de dados | **PostgreSQL** | |
| Cache e broker | **Redis** | |
| Jobs em background | **Celery** (worker + beat) | |
| Multi-tenancy | **Banco único**, schema compartilhado, coluna `tenant_id` | |
| Identificação do tenant | **Subdomínio** (`acme.dominio.com.br`) | Domínio próprio do cliente fica para o futuro |
| Observabilidade | Mínimo operacional no MVP; stack completa adiada | Ver `infraestrutura.md` |

### Alternativas consideradas

- **FastAPI + frontend separado:** descartado nesta fase. Exigiria montar auth, admin e migrations à mão, além de manter dois projetos.
- **Django API-only + Next.js:** descartado por ora pelo mesmo motivo de custo operacional. Continua possível como evolução (ver seção 9).
- **Schema por tenant (`django-tenants`):** isola mais, porém complica migrations e relatórios entre tenants. Reavaliar apenas se houver exigência de isolamento forte.

## 3. Estrutura do projeto

```
coworkhub/
├── config/                  # settings (base/dev/prod), urls, asgi/wsgi, celery
├── apps/
│   ├── tenants/             # Tenant, Domain, middleware, managers base
│   ├── accounts/            # User customizado, Membership (user ↔ tenant ↔ papel)
│   ├── spaces/              # Unidades, salas, mesas, recursos
│   ├── bookings/            # Reservas, regras de conflito, disponibilidade
│   ├── members/             # Perfil do membro / empresa residente
│   ├── plans/               # Planos operacionais, ciclos, créditos e consumo
│   ├── platform_billing/    # Assinatura SaaS do tenant (fora do MVP inicial)
│   ├── member_billing/      # Cobrança dos membros (evolução futura)
│   ├── access/              # Check-in e controle de acesso (evolução futura)
│   ├── notifications/       # E-mail e templates; outros canais no futuro
│   └── core/                # Mixins, utilitários, permissões
├── templates/
├── static/
├── docker-compose.yml
└── manage.py
```

### Organização interna de cada app

```
apps/bookings/
├── models.py          # dados e invariantes simples
├── services.py        # regras de negócio (create_booking, cancel_booking...)
├── selectors.py       # consultas complexas de leitura
├── forms.py           # validação de formulários (ModelForm)
├── views.py           # orquestra e devolve HTML (página ou fragmento)
├── urls.py
├── tasks.py           # jobs Celery
└── templates/bookings/
    ├── calendar.html
    └── partials/      # fragmentos trocados pelo HTMX
```

Regra de ouro: **regras que coordenam casos de uso vivem em `services.py`**, nunca em views ou templates. Invariantes locais simples também podem ser protegidas pelo model e, sempre que possível, por constraints do banco. Validações de interface (HTMX/Alpine) são estritamente para ergonomia e feedback visual de UX; **nenhuma regra de negócio ou integridade depende do frontend**. Toda e qualquer validação é obrigatoriamente reexecutada e garantida no backend (`forms.py`, `services.py` e constraints do PostgreSQL). Isso mantém o domínio independente da apresentação e facilita expor uma API no futuro.

## 4. Multi-tenancy

### 4.1 Modelos base

```python
# apps/tenants/models.py
class Tenant(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    # Ciclo de assinatura SaaS da plataforma (Asaas)
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ("trialing", "Trial (7 dias)"),
            ("active", "Assinatura Ativa"),
            ("past_due", "Pagamento Pendente"),
            ("canceled", "Cancelada"),
            ("expired", "Trial Expirado"),
        ],
        default="trialing"
    )
    trial_ends_at = models.DateTimeField()
    asaas_customer_id = models.CharField(max_length=100, blank=True)
    asaas_subscription_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_operational(self) -> bool:
        """Verifica se o tenant tem permissão para operar reservas e recursos."""
        return self.is_active and self.subscription_status in ("trialing", "active")

class Domain(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="domains")
    host = models.CharField(max_length=255, unique=True)  # ex: estacao-coworking.coworkhub.com.br
```

```python
# apps/core/exceptions.py
class TenantContextRequiredError(Exception):
    """Lançada quando uma query de TenantModel é executada sem tenant no contexto."""
    pass

# apps/core/models.py
from django.db import models
from apps.tenants.context import get_current_tenant
from apps.core.exceptions import TenantContextRequiredError

class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)

class TenantManager(models.Manager):
    """Manager padrão com comportamento Fail-Closed: sem tenant, levanta erro."""
    def get_queryset(self):
        tenant = get_current_tenant()
        if tenant is None:
            raise TenantContextRequiredError(
                f"Consulta em {self.model.__name__} executada sem tenant ativo no contexto."
            )
        return TenantQuerySet(self.model, using=self._db).filter(tenant=tenant)

class TenantModel(models.Model):
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        db_index=True
    )

    # Manager padrão: SEMPRE filtrado pelo tenant do contexto (Fail-Closed)
    objects = TenantManager()

    # Manager explícito para rotinas globais de suporte, migrations e admin interno
    global_objects = models.Manager()

    class Meta:
        abstract = True
        base_manager_name = "global_objects"  # Evita efeitos colaterais no Django Admin/ORM interno
```

Todo model de negócio (`Room`, `Booking`, `Plan`, ...) herda de `TenantModel`.

O model `Domain` existe separado de `Tenant` para permitir mais de um host por tenant (inclusive domínio próprio do cliente no futuro).

### 4.2 Geração de subdomínio e resolução por requisição

#### Geração e Validação do Slug a partir do Nome:
No onboarding, o comprador define o nome do seu espaço (ex: `"Estação Coworking"`). O backend processa e valida de forma autoritativa:
- **Normalização no Backend:** O service executa `slug = slugify(name)` (`"Estação Coworking"` → `"estacao-coworking"`).
- **Validação Autoritativa no Backend (`forms.py` / `services.py`):**
  1. Valida formato e caracteres permitidos (`^[a-z0-9]+(?:-[a-z0-9]+)*$`).
  2. Valida lista restrita de subdomínios reservados do sistema (`RESERVED_SUBDOMAINS`: `www`, `app`, `admin`, `api`, `status`, `mail`, `billing`, `webhook`, etc.).
  3. Checa colisão contra `Tenant` e `Domain` já cadastrados.
  4. Garante unicidade final no banco de dados via `UniqueConstraint` no PostgreSQL (`slug` e `host`).
- **Feedback Interativo de UX (HTMX):** O HTMX é utilizado estritamente como conveniência de interface: consulta o endpoint do backend enquanto o usuário digita para exibir feedback visual antecipado, mas o backend **sempre revalida 100% das regras no `POST`** do formulário de submissão.
- Registra o host `estacao-coworking.coworkhub.com.br`.

#### Roteamento no Middleware:

```
Requisição → TenantMiddleware →
   ├─ Host raiz / público (coworkhub.com.br, www.coworkhub.com.br) → request.tenant = None → Landing page / Onboarding
   └─ Subdomínio (acme.coworkhub.com.br) → Resolve Domain → Injeta request.tenant + ContextVar → App Operacional
```

```python
# apps/tenants/context.py
from contextvars import ContextVar
from contextlib import contextmanager

_current_tenant: ContextVar = ContextVar("current_tenant", default=None)

def get_current_tenant():
    return _current_tenant.get()

@contextmanager
def tenant_context(tenant):
    """Context manager para Celery tasks, comandos de terminal e testes."""
    token = _current_tenant.set(tenant)
    try:
        yield tenant
    finally:
        _current_tenant.reset(token)
```

- O middleware lê o host (`request.get_host()`).
- Se for domínio institucional (`coworkhub.com.br` ou `www.coworkhub.com.br`), define `request.tenant = None` e prossegue para as views públicas (landing, planos, onboarding).
- Se for subdomínio de cliente, busca o `Domain`. Se o tenant estiver com trial expirado ou assinatura cancelada, bloqueia o acesso dos membros e redireciona o `owner` para a tela de reativação de plano.
- O contexto é **obrigatoriamente limpo** no bloco `finally` do middleware (`_current_tenant.reset(token)`), mesmo em caso de erro.
- Tasks Celery sempre recebem `tenant_id` como argumento explícito e ativam o contexto via `with tenant_context(tenant):`.

### 4.3 Garantia de isolamento (Defesa em Profundidade)

Para garantir segurança rigorosa contra vazamento de dados entre tenants (*data leaks*), o sistema opera em camadas sobrepostas:

1. **Manager Fail-Closed no ORM:** O `objects.all()` padrão filtra pelo tenant ativo. Se não houver tenant definido, lança `TenantContextRequiredError` imediatamente, impedindo vazamentos silenciosos ou retornos acidentais de outros clientes. Consultas administrativas ou de suporte global devem usar explicitamente `Model.global_objects.all()`.
2. **Integridade Referencial Composta no PostgreSQL:** Ter `tenant_id` em duas tabelas não impede que uma reserva do Tenant A tente referenciar uma sala do Tenant B se um ID for forjado. Para blindar no banco:
   - Toda entidade expõe uma constraint única `UNIQUE (tenant_id, id)`.
   - Tabelas que referenciam entidades tenantizadas utilizam chave estrangeira composta:
     ```sql
     ALTER TABLE bookings_booking
     ADD CONSTRAINT fk_booking_resource_same_tenant
     FOREIGN KEY (tenant_id, resource_id)
     REFERENCES spaces_resource (tenant_id, id)
     ON DELETE CASCADE;
     ```
   Isso torna matematicamente impossível no PostgreSQL que uma entidade aponte para recursos de outro tenant.
3. **Row-Level Security (RLS) no PostgreSQL:** Proteção nativa adicional a nível de banco:
   - Ativado nas tabelas de negócio via migration: `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;`.
   - Política restritiva: `USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::integer)`.
   - O Django define `SET LOCAL app.current_tenant = %s` ao abrir transações/conexões (o uso de `SET LOCAL` restringe o valor à transação atual, sendo seguro contra contaminação de conexões reutilizadas).
4. **Isolamento obrigatório em Background Jobs:** Celery tasks nunca inferem tenant implicitamente; recebem `tenant_id` obrigatório e rodam encapsuladas por `with tenant_context(tenant):`.
5. **Harness de Testes de Isolamento Automatizados (`TenantIsolationTestCase`):** Classe base de testes obrigatória que inicializa dois tenants (`Tenant A` e `Tenant B`) e valida que qualquer tentativa de leitura, criação ou alteração cross-tenant falha categoricamente. IDs passados via URL ou payload são validados estritamente no escopo do tenant atual.

## 5. Usuários, papéis e autenticação

Um mesmo usuário pode participar de mais de um coworking, portanto o papel e o acesso não ficam no `User`:

```python
# apps/accounts/models.py
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=[("owner", "Dono"), ("staff", "Equipe"), ("member", "Membro")])
    unit = models.ForeignKey(
        "spaces.Unit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_memberships",
        help_text="Se nulo, papel é global no tenant. Se definido, restringe a atuação do staff a esta unidade/filial."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "tenant"], name="unique_user_tenant")
        ]
```

- **Papéis Fixos no MVP:** Para simplificar e acelerar a entrega do MVP, são adotados estritamente os 3 papéis nativos (`owner`, `staff`, `member`), sem permissões dinâmicas criadas pelo cliente. Criação de níveis customizados fica para evolução pós-MVP.
- **Filiais como Unidades (`Unit`):** Coworkings com filiais (ex: Matriz SP e Filial Recife) operam sob o mesmo `Tenant`, compartilhando marca, subdomínio e base de membros. O campo opcional `unit` permite alocar um funcionário `staff` para gerenciar apenas a sua respectiva filial.

### 5.1 Sessões, Cookies e CSRF em Multi-Subdomínio

- **`User` Customizado:** Login por e-mail, criado antes da primeira migração (`AUTH_USER_MODEL = "accounts.User"`).
- **Cookie de Sessão Compartilhado:**
  ```python
  SESSION_COOKIE_DOMAIN = ".coworkhub.com.br"
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_SAMESITE = "Lax"
  ```
  Isso viabiliza Single Sign-On (SSO): um usuário com memberships em mais de um coworking autentica uma única vez e navega entre os subdomínios dos tenants (`cowork1.coworkhub.com.br` e `cowork2.coworkhub.com.br`) sem refazer login.
- **Proteção CSRF em Subdomínios Dinâmicos:**
  ```python
  CSRF_TRUSTED_ORIGINS = ["https://*.coworkhub.com.br"]
  CSRF_COOKIE_DOMAIN = ".coworkhub.com.br"
  CSRF_COOKIE_SECURE = True
  ```
- **Autorização de Tenant via Middleware:**
  Estar autenticado como `User` não concede acesso automático ao tenant da requisição. O middleware valida:
  1. O usuário está autenticado?
  2. Existe `Membership` ativa para `(user=request.user, tenant=request.tenant)`?
  3. Se sim, injeta `request.membership` e `request.role`.
  4. Se não, bloqueia rotas operacionais do tenant com `403 Forbidden` amigável ("Você não possui vínculo ativo com este coworking").
- **Acesso do Suporte do Coworkhub:** O painel `/admin` do Django é restrito a superusuários internos do Coworkhub. Qualquer intervenção em dados de clientes deve gerar registro de auditoria com justificativa operacional.

## 6. Frontend

- Renderização no servidor com templates Django.
- **HTMX** para atualizações parciais: a view executa o service e devolve só o fragmento HTML, sem API JSON.
- **Alpine.js** para pequenas interações no cliente (dropdowns, modais, abas).
- **Tailwind CSS** para estilo (com DaisyUI ou similar, se desejado).

Exemplo (cancelar reserva sem recarregar a página):

```html
<button hx-post="{% url 'bookings:cancel' booking.id %}"
        hx-target="#booking-{{ booking.id }}"
        hx-swap="outerHTML">
  Cancelar
</button>
```

### Limitações conhecidas

- Telas muito interativas (calendário com arrastar e soltar, mapa de assentos em tempo real) dão mais trabalho que em React.
- Não há API pública no MVP. Um aplicativo mobile futuro exigirá expor endpoints (ver seção 9).

## 7. Módulos de domínio

| Módulo | Responsabilidade |
|---|---|
| `spaces` | Unidades, salas, mesas e recursos reserváveis |
| `bookings` | Reservas, regras de conflito, disponibilidade, cancelamento |
| `members` | Perfil de membros; empresas residentes são evolução futura |
| `plans` | Planos operacionais, ciclos, créditos, consumo e ajustes |
| `platform_billing` | Assinatura do Coworkhub cobrada do tenant |
| `member_billing` | Cobranças feitas pelo coworking aos seus membros |
| `access` | Check-in e controle de acesso, após o MVP |
| `notifications` | E-mail e templates; WhatsApp após o MVP |

Observações:

- **Planos operacionais e movimentos de uso devem estar no desenho do banco desde o início**, pois afetam como reservas consomem e estornam créditos ou horas.
- A assinatura SaaS do tenant (`platform_billing`) e a cobrança dos membros (`member_billing`) são contextos estritamente separados.
- Um **audit log por tenant** ("quem fez o quê") faz parte do MVP para ações críticas definidas em `dominio.md`.
- **LGPD:** não registrar dados pessoais sensíveis em logs (CPF, e-mail completo, dados de pagamento) e definir política de retenção.

### 7.1 Modelagem de Recursos: Salas vs Mesas

Para eliminar complexidade desnecessária no MVP e manter o motor de reservas unificado:
- Salas e Mesas são instâncias do modelo `Resource` com o atributo `resource_type` (`"room"` ou `"desk"`).
- **No MVP, cada mesa é modelada como uma posição individual exclusiva identificável** (ex: "Mesa 01", "Mesa 02", "Estação 3A").
- Dessa forma, salas e mesas compartilham **exatamente o mesmo fluxo de disponibilidade e o mesmo motor de concorrência**. Áreas de capacidade compartilhada sem assento definido (hot-desks em pool) ficam reservadas para evolução futura.

### 7.2 Concorrência, Conflitos e Transações de Reserva

A consulta de disponibilidade na interface ajuda a experiência do usuário, mas a exclusividade só é garantida no nível do PostgreSQL:

1. **Extensão `btree_gist` e Intervalo Semiaberto:**
   - Datas/horas são manipuladas em UTC e gravadas em intervalos semiabertos `[start_at, end_at)` via `tstzrange`.
2. **ExclusionConstraint no PostgreSQL:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS btree_gist;

   ALTER TABLE bookings_booking
   ADD CONSTRAINT exclude_overlapping_active_bookings
   EXCLUDE USING gist (
       resource_id WITH =,
       tstzrange(start_at, end_at, '[)') WITH &&
   )
   WHERE (status = 'confirmed');
   ```
   Isso garante, por construção matemática no banco de dados, que nenhuma reserva confirmada se sobreponha a outra no mesmo recurso, mesmo sob concorrência extrema de requisições simultâneas.
3. **Atomicidade da Reserva e Consumo:**
   A criação da reserva (`Booking`) e o lançamento do movimento de débito de créditos (`CreditMovement`) ocorrem dentro de `transaction.atomic()`. Se o membro não tiver saldo suficiente ou se o banco rejeitar a reserva por sobreposição, a transação sofre rollback integral.
4. **Proteção contra Duplo Clique (Idempotência):**
   O formulário de reserva gera um token único (`idempotency_key`). Em caso de duplo clique ou reenvio de pacote de rede, a aplicação detecta a requisição repetida e retorna a reserva já confirmada, sem duplicar o consumo do plano.

### 7.3 Faturamento da Plataforma (`platform_billing`) via Asaas (Adapter Pattern)

O faturamento da assinatura SaaS utiliza o padrão **Adapter / Gateway Interface** para desacoplar a lógica da aplicação do provedor de pagamento:

```python
# apps/platform_billing/gateways/base.py
from abc import ABC, abstractmethod

class BillingGateway(ABC):
    @abstractmethod
    def create_customer(self, name: str, email: str, cpf_cnpj: str, phone: str = "") -> str:
        """Cria o cliente e devolve o identificador do gateway."""
        pass

    @abstractmethod
    def create_subscription_with_trial(
        self,
        customer_id: str,
        value: float,
        credit_card_data: dict,
        trial_days: int = 7
    ) -> dict:
        """Valida e tokeniza o cartão de crédito e agenda a primeira cobrança para o 8º dia."""
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancela a assinatura no gateway."""
        pass
```

- **Implementação `AsaasBillingGateway`:**
  - Consome a API do **Asaas** (ambiente Sandbox em dev/testes e Produção em deploy).
  - Valida o cartão de crédito no momento do cadastro do coworking, garantindo que o cartão é autêntico e possui limite antes de liberar o trial de 7 dias.
- **Webhooks do Asaas:**
  - Endpoint público em `/webhooks/asaas/` protegido por validação de token secreto (`asaas-access-token`).
  - Eventos tratados assincronamente via Celery:
    - `PAYMENT_CONFIRMED`: Transiciona o `Tenant.subscription_status` para `active`.
    - `PAYMENT_OVERDUE`: Transiciona para `past_due` (inicia período de tolerância antes do bloqueio).
    - `SUBSCRIPTION_INACTIVATED` / `SUBSCRIPTION_DELETED`: Transiciona para `canceled` e bloqueia acesso operacional.

## 8. Ordem de construção sugerida

1. **Setup do projeto:** settings separados (base/dev/prod), `.env`, Docker Compose local (Postgres + Redis), `User` customizado.
2. **App `tenants`:** `Tenant`, `Domain`, middleware, `ContextVar`, `TenantModel` e testes de isolamento.
3. **App `accounts`:** `Membership`, login, convite de membros e permissões por papel.
4. **Telas base:** layout com Tailwind, navegação por papel e dashboard inicial.
5. **Configuração operacional:** unidades, salas, mesas, horários e bloqueios.
6. **Núcleo do produto:** reservas com proteção de concorrência e planos operacionais simples.
7. **Experiência:** dashboards da equipe e membro, audit log e notificações por e-mail.
8. **Produção piloto:** deploy, backups, observabilidade mínima e hardening (ver `infraestrutura.md`).

## 9. Evolução prevista

Como o domínio (models e services) é independente da apresentação, a evolução é de baixo risco:

1. **Fase 1:** Django fullstack com HTMX para as telas de gestão.
2. **Fase 2:** adicionar uma API (Django Ninja ou DRF) conforme surgirem necessidades (app mobile, portal do membro mais rico, integrações).
3. **Fase 3 (se fizer sentido):** migrar telas que exigem muita interatividade para um frontend separado, reaproveitando o backend.

## 10. Pontos em aberto

- Regras de tempo, consumo e cancelamento listadas em `mvp.md` (ver decisões sugeridas para fechamento do MVP).
- Limites entre `members`, `accounts` e futuros agrupamentos de empresas residentes.
- Estratégia de internacionalização; no MVP, os instantes são armazenados em UTC e exibidos no fuso do tenant.
