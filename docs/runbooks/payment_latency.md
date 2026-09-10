# Runbook: Degradação e Latência no Gateway de Pagamentos

> **Código do SOP:** SOP-PAY-003  
> **Serviço Alvo:** Payment Service & Webhook Workers  
> **Nível de Severidade:** P1  
> **Última Revisão:** 2026-09-09  

---

## 1. Descrição e Sintomas
Picos severos de tempo de resposta ou desconexões nos provedores de pagamento externos (adquirentes/gateways) gerando represamento de transações e falhas de checkout.

**Sintomas Comuns nos Logs:**
- `External payment gateway latency spike: p99 reached 12.4s`
- `ConnectionRefusedError: Failed to connect to payment acquirer socket`
- Acúmulo de mensagens pendentes na fila `payments.processing`.

---

## 2. Ações de Diagnóstico Recomendadas para o Agente
1. Consultar logs de conexão do payment worker via `query_logs`.
2. Verificar taxa de aprovação por adquirente no painel de pagamentos.
3. Avaliar saturação de conexões de banco de dados do microsserviço de pagamentos.

---

## 3. Procedimento de Mitigação (Requer HITL)
1. **Comutar Adquirente Primário (Failover Inteligente):**
   - Redirecionar 100% do tráfego para a adquirente secundária via feature flag dinâmico.
2. **Ativar Retentativas Exponenciais com Jitter:**
   - Evitar saturação da fila de transações pendentes.
