# Runbook: Timeout e Falha em Cascata no Checkout

> **Código do SOP:** SOP-API-001  
> **Serviço Alvo:** Checkout API & Inventory Service  
> **Nível de Severidade:** P0 / P1  
> **Última Revisão:** 2026-09-09  

---

## 1. Descrição e Sintomas
O serviço de checkout experimenta esgotamento de threads e timeouts (HTTP 504 / 500) devido a lentidão extrema no microsserviço de inventário upstream durante a reserva de itens.

**Sintomas Comuns nos Logs:**
- `GatewayTimeout: Upstream inventory-service timed out after 3000ms at /api/v1/stock/reserve`
- `CircuitBreakerOpenException: inventory-service circuit opened`
- Queda abrupta na taxa de conversão de compras e aumento de latência p99 > 8000ms.

---

## 2. Ações de Diagnóstico Recomendadas para o Agente
1. Verificar status de deployments de checkout e inventário via `check_k8s_deployment_health`.
2. Avaliar taxa de erro 504 nos logs do proxy via `query_logs`.
3. Inspecionar se há locks de inventário no banco de dados.

---

## 3. Procedimento de Mitigação (Requer HITL)
1. **Ativar Fallback Assíncrono no Checkout:**
   - Comutar o checkout para modo de reserva assíncrona temporária via fila RabbitMQ/Kafka.
2. **Circuit Breaker Activation:**
   - Forçar abertura do circuit breaker do inventário para responder com estoque estimado ou cache Redis.
3. **Escalar Deployment:**
   - `kubectl scale deployment inventory-service --replicas=6`
