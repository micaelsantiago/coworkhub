# Coworkhub: visão do produto

## 1. Visão

O Coworkhub é uma plataforma SaaS B2B para coworkings pequenos e médios administrarem unidades, membros, salas, mesas e reservas em um único lugar.

A primeira versão substitui controles fragmentados — como planilhas, agendas e conversas por WhatsApp — por uma fonte confiável de disponibilidade. A equipe mantém o controle da operação, enquanto membros conseguem consultar horários e reservar recursos por conta própria.

## 2. Público inicial

### Cliente

Empresa de coworking pequena ou média, com uma ou poucas unidades, que ainda possui processos manuais ou ferramentas desconectadas.

### Comprador provável

- dono do coworking;
- gestor de operações;
- responsável administrativo.

### Usuários

| Ator | Necessidade principal |
|---|---|
| Dono | Configurar a operação e acompanhar a utilização das unidades |
| Equipe | Cadastrar membros, administrar recursos e intervir em reservas |
| Membro | Consultar disponibilidade e gerenciar as próprias reservas |
| Suporte Coworkhub | Prestar suporte controlado e auditável aos tenants |

Os papéis e suas permissões detalhadas estão descritos em `dominio.md`.

## 3. Problema

Operações manuais de reserva costumam gerar:

- conflitos de horário e reservas duplicadas;
- demora para confirmar disponibilidade;
- dependência da equipe para tarefas simples;
- pouca visibilidade sobre utilização de salas e mesas;
- dificuldade para aplicar limites de planos de forma consistente;
- histórico disperso de alterações e cancelamentos.

## 4. Proposta de valor

Para o coworking:

- centralizar disponibilidade e reservas;
- reduzir trabalho manual da equipe;
- aplicar regras e limites de forma consistente;
- manter histórico operacional por unidade e membro;
- permitir crescimento sem multiplicar planilhas e agendas.

Para o membro:

- consultar disponibilidade em tempo real;
- reservar sem aguardar atendimento;
- visualizar limites e consumo do plano;
- cancelar conforme as regras do coworking.

## 5. Posicionamento inicial

O Coworkhub começa como uma ferramenta de **operação e reservas**, não como um ERP completo nem como um marketplace de espaços.

O diferencial a validar é a combinação de:

- implantação simples para operações pequenas e médias;
- experiência direta para equipe e membros;
- regras de reserva e limites de uso adequados a coworkings;
- preço previsível por unidade.

Esse posicionamento é uma hipótese e deve ser validado com clientes-piloto e análise de concorrentes.

## 6. Modelo comercial

- **Assinatura da Plataforma:** Mensalidade cobrada pelo Coworkhub de cada empresa de coworking (tenant), processada via gateway **Asaas**.
- **Trial de 7 Dias com Cartão Prévio:** O cliente inicia com um período de testes gratuito de 7 dias. O cartão de crédito é cadastrado e validado no momento do onboarding, ocorrendo a primeira cobrança recorrente no 8º dia caso não haja cancelamento prévio.
- **Onboarding Self-Service com Subdomínio Próprio:** O comprador acessa a página pública, define o nome do coworking (ex: "Estação Coworking"), o sistema gera automaticamente o subdomínio (`estacao-coworking.coworkhub.com.br`), valida o cartão e libera o ambiente imediatamente.

Devem permanecer rigorosamente separados no produto e no código:

1. **Cobrança da plataforma:** Coworkhub cobra o tenant pelo uso do SaaS (módulo `platform_billing`).
2. **Cobrança dos membros:** O coworking cobra seus clientes por planos ou reservas (continua manual/externo no MVP, módulo `member_billing`).

## 7. Princípios de produto

1. **Operação primeiro:** resolver bem reservas antes de ampliar para financeiro e acesso físico.
2. **Sem conflito silencioso:** uma reserva confirmada representa disponibilidade garantida segundo as regras cadastradas.
3. **Tenant no centro:** nenhum dado ou ação pode atravessar empresas de coworking.
4. **Autonomia com controle:** o membro se atende sozinho, e a equipe conserva capacidade de administração.
5. **Evolução incremental:** integrações só entram quando houver demanda validada.
6. **Privacidade por padrão:** coletar apenas dados necessários e evitar dados pessoais em logs.

## 8. Indicadores de sucesso

Os valores-alvo devem ser definidos após medir a operação dos clientes-piloto.

Indicadores candidatos:

- percentual de reservas feitas pelos próprios membros;
- tempo médio para concluir uma reserva;
- quantidade de conflitos ou intervenções manuais;
- reservas por unidade e por recurso;
- taxa de cancelamento e no-show, quando disponível;
- membros ativos no período;
- ativação de novos tenants e tempo até a primeira reserva;
- retenção e cancelamento de tenants.

## 9. Fora do posicionamento inicial

- marketplace público de coworkings;
- contabilidade ou ERP completo;
- emissão fiscal;
- controle físico de acesso;
- aplicativo móvel nativo;
- gestão avançada de eventos;
- automações complexas de marketing.

Essas capacidades podem ser reavaliadas após validação do núcleo do produto.

## 10. Questões abertas

- Qual é o tamanho típico dos primeiros clientes em unidades, membros e reservas?
- Qual processo atual causa mais custo ou insatisfação?
- Quais concorrentes são usados ou avaliados por esses clientes?
- Qual preço por unidade é aceitável?
- O tenant pode contratar apenas algumas unidades e manter outras inativas?
- Que dados precisam ser importados durante o onboarding?
- Qual nível de suporte e disponibilidade será prometido?
