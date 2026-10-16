# Coworkhub: domínio e regras de negócio

## 1. Objetivo

Este documento define o vocabulário comum e as invariantes do domínio. Ele orienta produto, implementação e testes, mas não substitui o modelo físico do banco.

## 2. Contextos do produto

### Operação do coworking

Abrange tenants, unidades, membros, espaços, planos de uso, disponibilidade e reservas. É o núcleo do MVP.

### Cobrança dos membros

Abrange valores que o coworking cobra de seus membros. No MVP, a aplicação registra apenas direitos e limites operacionais; pagamento e conciliação ficam fora do sistema.

### Cobrança da plataforma

Abrange a assinatura que o tenant paga ao Coworkhub, inicialmente calculada por unidade. Deve ser isolada da cobrança dos membros, inclusive em nomenclatura, permissões e dados.

## 3. Vocabulário

| Termo | Definição |
|---|---|
| Tenant | Empresa de coworking cliente do Coworkhub e fronteira principal de isolamento |
| Unidade | Local físico operado por um tenant |
| Usuário | Identidade global que autentica por e-mail |
| Membership | Vínculo de um usuário com um tenant, incluindo papel e estado |
| Membro | Participante do coworking autorizado a utilizar recursos |
| Recurso | Item reservável pertencente a uma unidade |
| Sala | Recurso normalmente exclusivo durante um intervalo |
| Mesa | Posição individual de trabalho exclusiva e identificável vinculada a uma unidade |
| Plano operacional | Conjunto de direitos e limites de uso, sem implicar pagamento confirmado |
| Ciclo de uso | Período no qual uma franquia é concedida e consumida |
| Movimento | Crédito, consumo, estorno ou ajuste que altera o saldo de uso |
| Reserva | Alocação de um recurso para um membro em um intervalo |
| Bloqueio | Indisponibilidade operacional que impede reservas |
| Audit log | Registro imutável de uma ação relevante e de seu ator |

## 4. Relações principais

```text
Tenant
├── Domain
├── Unit
│   └── Resource (Room ou Desk)
├── Membership ── User
├── OperationalPlan
├── PlanAssignment ── Membership
├── UsageCycle
│   └── CreditMovement
└── Booking ── Resource + Membership
```

Todas as entidades operacionais pertencem diretamente a um tenant, mesmo quando o tenant também pode ser inferido por outra relação. Essa redundância facilita filtragem e proteção, mas exige garantia de consistência entre as referências.

## 5. Entidades e responsabilidades

### Tenant e Domain

- `Tenant` representa a empresa cliente e a fronteira principal de isolamento.
- Possui ciclo de assinatura do SaaS (`subscription_status`):
  - `trialing`: Período gratuito de 7 dias com cartão de crédito previamente validado; acesso 100% liberado.
  - `active`: Assinatura recorrente ativa e paga via gateway (Asaas); acesso liberado.
  - `past_due`: Falha de cobrança na renovação; gera aviso na interface e período de tolerância.
  - `expired`: Período de 7 dias esgotado sem confirmação de pagamento; bloqueia membros e redireciona o `owner` para reativação.
  - `canceled`: Assinatura cancelada; acesso operacional bloqueado.
- O slug do `Tenant` é derivado diretamente do nome comercial informado pelo usuário no cadastro (ex: "Estação Coworking" gera o slug `"estacao-coworking"` e o host `"estacao-coworking.coworkhub.com.br"`), com normalização de acentos e caracteres especiais. A validação de formato, unicidade e proibição de nomes reservados é uma invariante obrigatória do backend e do banco de dados (o feedback de interface via HTMX é apenas assistivo).
- `Domain` resolve o subdomínio para exatamente um tenant. Slugs reservados do sistema são expressamente proibidos.

### Unit

- pertence a exatamente um tenant;
- representa uma localização física (matriz ou filial, ex: Matriz SP e Filial Recife);
- filiais de uma mesma empresa pertencem ao mesmo tenant, compartilhando o mesmo subdomínio e base de membros;
- possui endereço, fuso horário e horários de funcionamento próprios;
- pode ser desativada sem apagar histórico de reservas.

### User e Membership

- `User` é global e o e-mail é sua identidade de autenticação;
- `Membership` define acesso a um tenant específico;
- o mesmo usuário pode ter memberships em tenants diferentes;
- deve existir no máximo uma membership por par usuário/tenant;
- desativar uma membership bloqueia novas ações, sem remover reservas históricas.

Papéis fixos no MVP (sem criação dinâmica de níveis pelo usuário para simplificar a entrega inicial):

| Papel | Responsabilidade |
|---|---|
| `owner` | Dono/administrador geral: gerencia o tenant, faturamento SaaS no Asaas, filiais (`Units`), equipe e regras |
| `staff` | Operação diária: gerencia membros, salas, mesas, reservas e bloqueios. Pode atuar em todo o tenant ou ter escopo restrito a uma filial (`Unit`) |
| `member` | Cliente do coworking: autoatendimento de reservas e consulta de saldo de planos |

Níveis de acesso customizados com matriz dinâmica de permissões ficam para evolução pós-MVP.

### Resource

- pertence ao mesmo tenant de sua unidade;
- é do tipo sala ou mesa no MVP; ambos operam como recursos exclusivos identificáveis;
- só aceita novas reservas quando ativo;
- granularidade mínima padrão de 30 minutos;
- desativação não remove reservas passadas.

### OperationalPlan e PlanAssignment

- o plano descreve uma franquia simples de horas por ciclo mensal (mês-calendário);
- saldo não utilizado no fim do mês expira automaticamente (não cumulativo);
- a atribuição associa o plano a uma membership por um período;
- alterações de plano não devem reescrever consumo histórico;
- saldo é derivável exclusivamente do somatório de movimentos em `CreditMovement`, evitando contadores mutáveis sem histórico.

Tipos mínimos de movimento:

- concessão de franquia;
- consumo por reserva;
- estorno por cancelamento;
- ajuste manual, sempre com motivo e ator.

### Booking

Campos conceituais mínimos:

- tenant;
- unidade e recurso;
- membership beneficiária;
- ator que criou a reserva;
- início e fim;
- estado;
- consumo associado;
- timestamps e motivo de cancelamento, quando aplicável.

Estados iniciais sugeridos:

```text
confirmed → cancelled
confirmed → completed
confirmed → no_show     (futuro ou após definição operacional)
```

Não é necessário um estado `pending` enquanto não houver aprovação manual ou processamento assíncrono da confirmação.

### Block

- torna um recurso indisponível em um intervalo;
- pertence ao mesmo tenant e unidade do recurso;
- registra motivo e ator;
- não deve cancelar silenciosamente reservas já confirmadas.

## 6. Invariantes

### Isolamento

1. Toda operação ocorre no contexto de exatamente um tenant.
2. Ausência de contexto deve falhar de forma fechada nas consultas tenantizadas.
3. Uma entidade nunca referencia entidade operacional de outro tenant.
4. Autorizações consideram a membership ativa no tenant atual.
5. IDs fornecidos pelo cliente nunca substituem a filtragem por tenant.

### Reservas

1. `start_at < end_at`.
2. Instantes são persistidos em UTC e exibidos no fuso do tenant.
3. Intervalos usam a convenção semiaberta `[início, fim)`, permitindo reservas adjacentes.
4. Reservas confirmadas incompatíveis não se sobrepõem para o mesmo recurso.
5. Bloqueios incompatíveis impedem confirmação no intervalo.
6. A criação da reserva e seu consumo são uma única operação transacional.
7. Repetir uma mesma requisição não pode gerar cobrança ou consumo duplicado.
8. Cancelamento preserva a reserva e gera movimento de estorno quando a política permitir.
9. A proteção contra concorrência deve existir no PostgreSQL, não apenas em uma consulta anterior ao `save`.

### Auditoria

Devem registrar ator, tenant, momento e contexto mínimo:

- alterações de papéis e status de memberships;
- ajustes de saldo;
- criação ou cancelamento administrativo de reservas;
- override de regras;
- mudanças relevantes em planos e recursos.

O audit log não deve armazenar segredos ou dados pessoais desnecessários.

## 7. Consistência e concorrência

O fluxo de confirmação deve executar em transação e validar:

1. tenant e membership ativos;
2. recurso ativo e pertencente ao tenant/unidade;
3. horário operacional e ausência de bloqueio;
4. ausência de conflito;
5. direito de uso e saldo suficiente;
6. criação da reserva e do movimento de consumo.

Para recursos exclusivos (salas e mesas), a proteção contra sobreposição é garantida no PostgreSQL via `ExclusionConstraint` com tipo de intervalo temporal `tstzrange` e extensão `btree_gist`. Validações na camada de aplicação servem para feedback amigável ao usuário, mas a garantia de concorrência é do banco de dados.

## 8. Eventos de domínio candidatos

Eventos internos ajudam a desacoplar notificações sem transformar o monolito em microsserviços:

- `member_invited`;
- `booking_confirmed`;
- `booking_cancelled`;
- `usage_adjusted`.

E-mails podem ser enfileirados após o commit da transação. Falha de notificação não deve desfazer uma reserva confirmada.

## 9. Regras de negócio e parâmetros fechados para o MVP

1. **Semântica de Mesas:** Cada mesa é uma posição individual exclusiva identificável (ex: "Mesa 01", "Mesa 02"). Salas e mesas compartilham o mesmo motor de disponibilidade e exclusão temporal.
2. **Escopo dos Planos:** Limitam horas gerais de uso por mês. 1 hora reservada = 1 hora consumida da franquia.
3. **Granularidade e Duração:**
   - Granularidade mínima: 30 minutos (sempre em blocos de 30 min, arredondando qualquer fração para cima).
   - Duração da reserva: mínimo de 30 minutos e máximo de 4 horas contínuas por sala.
4. **Janela de Agendamento:**
   - Antecedência mínima: 15 minutos antes do horário de início.
   - Antecedência máxima: até 30 dias no futuro.
5. **Política de Cancelamento e Estorno:**
   - Cancelamento com **>= 2 horas de antecedência:** gera estorno integral das horas consumidas (`movement_type = 'refund'`).
   - Cancelamento com **< 2 horas:** a reserva muda para `cancelled` liberando o espaço, mas as horas permanecem consumidas.
6. **Tratamento de No-Show:**
   - A equipe pode sinalizar a reserva como `no_show` após 30 minutos de atraso, liberando o recurso para novos agendamentos sem devolução de saldo.
7. **Ciclo de Uso e Renovação:**
   - Ciclos baseados em mês-calendário (renovação automática no 1º dia de cada mês). Saldo não consumido **não acumula** para o ciclo seguinte.
   - Cada membro possui apenas um plano atribuído por tenant por período.
8. **Overrides Operacionais:**
   - Apenas `owner` e `staff` podem realizar reservas com override de saldo ou antecedência; a justificativa é obrigatória e gravada em `AuditLog`.
9. **Bloqueios Operacionais com Reservas Existentes:**
   - Um bloqueio operacional (`Block`) não cancela silenciosamente reservas ativas. Se houver reservas no período a ser bloqueado, o sistema alerta os conflitos e exige que a equipe cancele ou remaneje manualmente as reservas antes de ativar o bloqueio.
10. **Empresas Residentes:**
    - Não constituem entidade isolada no MVP. Todos os membros autenticam como indivíduos com sua respectiva `Membership`. Agrupamento por empresa residente fica para evolução futura.
