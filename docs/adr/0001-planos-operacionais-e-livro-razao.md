# 0001. Planos Operacionais dos Membros e Livro-Razão de Créditos

**Status:** accepted  
**Data:** 2026-10-16  
**Decisores:** Time de Produto e Engenharia  
**Contexto Técnico:** Módulo de Planos (`apps.plans`), Reservas (`apps.bookings`) e Contas (`apps.accounts`)

---

## Decisão

Para gerenciar o direito de reserva de salas e cabines sem risco de corrupção de saldo por concorrência e com isolamento fail-closed, adotamos um **modelo de livro-razão imutável (`CreditMovement`)** atrelado à `Membership` individual, com ciclo estrito por **mês-calendário** e equivalência direta de **1 hora de sala = 1 hora de franquia**. 

O autoatendimento bloqueia novas reservas ao esgotar o saldo (fail-closed), enquanto a equipe pode realizar overrides com justificativa obrigatória no audit log, gerando saldo negativo para faturamento manual externo. Mesas físicas (dedicadas ou rotativas) operam fora da franquia de horas.

---

## Opções Consideradas

1. **Contador Mutável de Saldo (`saldo_horas` atualizado por `UPDATE`)**:
   * *Rejeitado:* Apresenta alto risco de condições de corrida (*race conditions*) em concorrência, perda de rastreabilidade de estornos e impossibilidade de auditar o extrato histórico do membro de forma determinística.
2. **Sistema de Créditos com Pesos Diferenciados por Sala (Ex: Sala VIP = 2 créditos/h, Cabine = 0.5 créditos/h)**:
   * *Rejeitado para o MVP:* Introduziria complexidade matemática desnecessária e atrito cognitivo para o membro no autoatendimento. A regra 1 hora = 1 hora é transparente e atende a grande maioria dos coworkings independentes.
3. **Bolsão de Horas Compartilhado por Empresa (Contas Corporativas)**:
   * *Rejeitado para o MVP:* Modelar hierarquias de empresas-clientes com múltiplos membros consumindo da mesma franquia aumentaria a complexidade relacional e transacional antes de validar o núcleo do produto. O plano é atribuído individualmente à `Membership`.
4. **Abatimento de Saldo Negativo na Virada de Mês**:
   * *Rejeitado:* Como o Coworkhub não realiza cobrança financeira de membros no MVP, abater horas negativas na virada de ciclo geraria atrito para a equipe (que já cobra as horas extras no balcão/fatura manual) e descompasso com a mensalidade fixa contratada. O novo mês inicia com a franquia cheia.

---

## Consequências e Regras Arquiteturais

* **Cálculo Derivado de Saldo:** O saldo disponível de um membro é sempre calculado pela soma das movimentações (`Sum(amount)`) do ciclo vigente, nunca por um campo de valor mutável em tabela.
* **Tipos Canônicos de Movimento:**
  * `ALLOWANCE`: Concessão da franquia mensal ou pro-rata de entrada no meio do mês.
  * `BOOKING`: Débito transacional de horas por reserva confirmada.
  * `REFUND`: Estorno por cancelamento qualificado com $\ge 2$ horas de antecedência (vinculado obrigatoriamente à reserva cancelada).
  * `EXPIRATION`: Zeramento de saldo residual não consumido no fim do mês.
  * `ADJUSTMENT`: Ajuste manual pela recepção com justificativa e autor registrados.
* **Serialização e Concorrência:** Toda validação de saldo e criação de reserva deve executar sob bloqueio pessimista de linha (`select_for_update`) na `Membership`, impedindo que requisições paralelas furem a franquia.
* **Reservas Inter-Meses:** Agendamentos futuros consom a franquia do mês em que o evento ocorrerá (`start_time.month`), impedindo o uso de saldo residual prestes a expirar para reservar datas futuras.
* **Rotina de Virada de Mês:** Job agendado no Celery Beat (00:01 do 1º dia de cada mês no fuso horário da unidade) gera explicitamente os movimentos de `EXPIRATION` do saldo remanescente e `ALLOWANCE` da nova franquia para todos os membros ativos.
* **Desativação de Membro:** O cancelamento de contrato ou desativação de uma `Membership` cancela automaticamente todas as suas reservas futuras, liberando as salas na agenda imediatamente.
