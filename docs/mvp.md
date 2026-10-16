# Coworkhub: escopo do MVP

## 1. Objetivo

Entregar a coworkings pequenos e médios uma operação básica de reservas confiável, na qual a equipe configura unidades, salas, mesas, membros e limites, e os membros consultam disponibilidade e administram suas próprias reservas.

O MVP deve validar que o autoatendimento reduz trabalho manual sem retirar o controle operacional da equipe.

## 2. Escopo funcional

### 2.1 Tenant, Onboarding e Assinatura

- **Onboarding self-service:** cadastro público do coworking no portal raiz (`coworkhub.com.br`);
- **Geração automática de subdomínio:** o slug é gerado a partir do nome informado pelo usuário (ex: "Estação Coworking" gera o slug `estacao-coworking` e a URL `estacao-coworking.coworkhub.com.br`), com normalização e validação autoritativa no backend (formato, unicidade e lista de termos reservados), acompanhada de feedback visual assistivo de UX no frontend;
- **Trial de 7 dias com cartão prévio:** cadastro e validação de cartão de crédito no gateway **Asaas** no momento do signup; primeira cobrança disparada automaticamente no 8º dia;
- **Provisionamento instantâneo:** subdomínio imediatamente acessível após cadastro (via wildcard Cloudflare);
- **Configurações da empresa:** definir fuso horário e dados básicos da operação;
- **Cadastrar unidades e filiais:** suporte a uma ou mais unidades físicas do coworking (matriz e filiais sob a mesma empresa, marca e subdomínio).

### 2.2 Usuários e membros

- autenticação por e-mail e senha;
- cadastro ou convite de membros pela equipe do coworking (sem cadastro público aberto de membros);
- aceite de convite e definição de senha;
- vínculo do mesmo usuário com mais de um tenant;
- papéis fixos para simplificação do MVP: `owner`, `staff` (com suporte a escopo global ou restrito por filial) e `member` (níveis de acesso dinâmicos ficam para evolução pós-MVP);
- ativação e desativação de vínculos sem apagar o histórico.

### 2.3 Espaços e recursos

- cadastrar salas e mesas vinculadas a uma unidade;
- definir nome, descrição, capacidade e estado ativo/inativo;
- configurar horários básicos de disponibilidade;
- bloquear um recurso por manutenção ou indisponibilidade operacional.

Equipamentos, serviços, auditórios e eventos não fazem parte do MVP, embora o modelo possa evoluir para outros tipos de recurso.

### 2.4 Planos e limites

- associar um membro a um plano operacional;
- definir franquia simples de horas ou créditos por período;
- consultar saldo e consumo;
- registrar ajustes manuais feitos pela equipe com motivo e autoria;
- devolver ou não o consumo em cancelamentos conforme uma política definida.

Pagamento online, cobrança recorrente e emissão de faturas não fazem parte do MVP. O plano representa o direito de uso, não a confirmação de pagamento.

### 2.5 Reservas

- consultar disponibilidade de salas e mesas;
- criar reserva para um intervalo de tempo;
- confirmar automaticamente quando houver disponibilidade e direito de uso;
- impedir sobreposição incompatível;
- listar próximas reservas e histórico;
- permitir que o membro cancele a própria reserva conforme a política;
- permitir que a equipe crie e cancele reservas em nome de membros;
- registrar autoria e eventos relevantes da reserva.

Recorrência, lista de espera e aprovação manual ficam fora do primeiro recorte.

### 2.6 Comunicação

- enviar e-mail de convite;
- enviar confirmação e cancelamento de reserva;
- permitir reenvio controlado quando necessário.

WhatsApp, SMS e campanhas ficam para uma etapa posterior.

### 2.7 Operação e suporte

- dashboard simples com reservas do dia e próximos horários;
- administração dos cadastros pela interface do produto;
- audit log mínimo para ações críticas;
- painel Django restrito ao suporte interno do Coworkhub.

## 3. Jornadas principais

### 3.1 Configurar um coworking

1. O comprador acessa o portal público (`coworkhub.com.br`) e escolhe o plano do SaaS.
2. Informa o nome do coworking (ex: "Estação Coworking") e seus dados de acesso (nome, e-mail e senha).
3. O backend normaliza o nome, gera o slug (`estacao-coworking`) e valida a conformidade e unicidade do subdomínio `estacao-coworking.coworkhub.com.br` (com feedback interativo de UX via HTMX na interface).
4. O comprador insere os dados do cartão de crédito para iniciar o trial de 7 dias (validado e tokenizado via **Asaas** Sandbox/Prod).
5. O sistema provisiona em transação única o `Tenant`, o `Domain`, o `User` e a `Membership` (`owner`), registrando o trial de 7 dias.
6. O dono é redirecionado imediatamente para `https://estacao-coworking.coworkhub.com.br` já autenticado.
7. Cadastra a unidade, horários de funcionamento, salas e mesas.
8. Cria ao menos um plano operacional e cadastra/convida os membros.
9. O coworking está operacional quando um membro visualiza a disponibilidade e realiza a primeira reserva.

### 3.2 Membro faz uma reserva

1. O membro entra no subdomínio do coworking.
2. Seleciona unidade, data, horário e tipo de recurso.
3. O sistema apresenta recursos disponíveis.
4. O membro escolhe um recurso e confirma.
5. O sistema valida vínculo, status, horário, conflito e limite do plano em uma única operação transacional.
6. A reserva é confirmada e o consumo é registrado.
7. O membro recebe a confirmação na interface e por e-mail.

### 3.3 Equipe intervém em uma reserva

1. A equipe localiza o membro ou a reserva.
2. Cria ou cancela a reserva com permissão apropriada.
3. Quando houver exceção de limite, informa o motivo.
4. O sistema registra ator, momento, ação e justificativa.

### 3.4 Cancelar uma reserva

1. O ator solicita o cancelamento.
2. O sistema verifica permissão e política de cancelamento.
3. A reserva muda de estado sem perder o histórico.
4. O consumo é devolvido ou mantido conforme a política.
5. O cancelamento é comunicado ao membro.

## 4. Critérios de conclusão do MVP

O MVP estará funcionalmente pronto quando:

- um novo tenant puder ser configurado sem alteração manual no banco;
- equipe e membros só enxergarem dados de tenants aos quais pertencem;
- duas requisições concorrentes não puderem confirmar reservas incompatíveis;
- as regras de limite e cancelamento tiverem resultados determinísticos;
- ações administrativas críticas forem auditáveis;
- o fluxo principal funcionar em telas móveis e desktop;
- backup, restauração e deploy estiverem documentados e testados;
- erros da aplicação e falhas de jobs gerarem sinal operacional.

## 5. Entregas sugeridas

1. **Fundação:** projeto, tenant, usuário, autenticação, isolamento e testes.
2. **Configuração operacional:** unidades, recursos, horários e bloqueios.
3. **Membros:** convites, vínculos, papéis e desativação.
4. **Reservas:** disponibilidade, criação, concorrência, cancelamento e histórico.
5. **Planos simples:** limite, consumo, estorno e ajustes.
6. **Experiência e comunicação:** dashboards, e-mails e refinamento responsivo.
7. **Piloto:** deploy, observabilidade mínima, backup e onboarding do primeiro cliente.

## 6. Não objetivos do MVP

- gateway de pagamento e cobrança automática;
- cobrança do SaaS totalmente automatizada;
- nota fiscal;
- domínio próprio do tenant;
- aplicativo nativo ou API pública;
- reservas recorrentes;
- aprovação manual configurável;
- controle físico de acesso e QR code;
- WhatsApp;
- relatórios avançados;
- internacionalização completa;
- importações genéricas para qualquer sistema de origem.

## 7. Hipóteses a validar no piloto

- membros preferem autoatendimento a solicitar reserva à equipe;
- limites simples atendem aos planos dos coworkings iniciais;
- salas e mesas compartilham regras suficientes para o mesmo fluxo;
- cobrança manual dos membros não impede adoção;
- mensalidade por unidade é percebida como simples e justa;
- o onboarding pode ser concluído sem consultoria extensa.

## 8. Decisões e parâmetros fechados para implementação do MVP

Os pontos que bloqueavam a modelagem física do banco e a lógica de serviços foram formalmente definidos para o MVP:

1. **Unidade mínima e granularidade:** Blocos de 30 minutos. Frações parciais são arredondadas para cima em múltiplos de 30 minutos.
2. **Janela de agendamento:** Antecedência mínima de 15 minutos e máxima de 30 dias no futuro.
3. **Duração da reserva:** Mínimo de 30 minutos e máximo de 4 horas contínuas por sala (evitando reservas abusivas de dia inteiro sem aprovação).
4. **Política de cancelamento:** 
   - Cancelamento com **>= 2 horas de antecedência:** 100% das horas são estornadas ao plano.
   - Cancelamento com **< 2 horas de antecedência:** o espaço é liberado na agenda, mas o consumo do plano é mantido.
5. **Tratamento de no-show:** Tolerância de 30 minutos após o início da reserva. A equipe pode marcar o status como `no_show`, liberando o recurso para outros membros sem restituição de horas.
6. **Modelagem de mesas:** Posições individuais de trabalho exclusivas e numeradas (ex: "Mesa 01", "Mesa 02"), compartilhando as mesmas regras e motor de concorrência das salas.
7. **Bloqueios operacionais:** A criação de um bloqueio não cancela reservas existentes silenciosamente. O sistema acusa o conflito e exige cancelamento ou remanejamento assistido pela equipe.
8. **Override pela equipe:** Papéis `owner` e `staff` podem criar reservas com override de limites de saldo ou janelas de antecedência, sendo obrigatório registrar a justificativa no `AuditLog`.
9. **Renovação de limites:** Ciclo mensal baseado em mês-calendário (renovação automática no 1º dia de cada mês).
10. **Saldo residual:** Saldo de horas não consumido ao fim do mês expira automaticamente (não acumula para o ciclo seguinte).
