"""Chaos Studio & Zero-Token Replay Mode for OpsMesh.

Provides 4 canonical production crisis scenarios and a Zero-Token Replay Sandbox
allowing interactive evaluation and demo execution without incurring LLM API costs.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from pydantic import BaseModel, Field

from opsmesh.core.schemas import IncidentResponse

logger = logging.getLogger(__name__)


class ChaosScenario(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    service: str
    alert_payload: dict[str, Any]
    expected_root_cause: str
    cached_replay_response: dict[str, Any] = Field(default_factory=dict)


SCENARIOS: dict[str, ChaosScenario] = {
    "postgres-pool": ChaosScenario(
        id="postgres-pool",
        title="Saturação e Esgotamento do Pool de Conexões PostgreSQL",
        description="Fila de requisições travada no order-service com 98% das conexões em 'idle in transaction'.",
        severity="P0_CRITICAL",
        service="order-service",
        expected_root_cause="PostgreSQL pool exhausted with 98% saturation and 36 waiting connections",
        alert_payload={
            "service": "order-service",
            "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections on db-primary (10.0.4.15)",
            "severity": "P0_CRITICAL",
            "source": "datadog",
            "details": {"active_connections": 98, "max_connections": 100},
        },
        cached_replay_response={
            "incident_id": "INC-REPLAY-PG-01",
            "severity": "P0_CRITICAL",
            "status": "AWAITING_APPROVAL",
            "root_cause_summary": "Logs: Detectados erros críticos concentrados no serviço 'order-service': FATAL: remaining connection slots are reserved e Infra: PostgreSQL com 98.0% de utilização do pool e 36 conexões em espera.",
            "remediation_plan": {
                "action_type": "DATABASE_TERMINATE_BACKENDS",
                "is_critical_action": True,
                "risk_level": "HIGH",
                "proposed_commands": [
                    "POST /operations/mitigate (target_action: DATABASE_CONNECTION_SCALE)",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction';",
                    "kubectl rollout restart deployment chaos-lab -n production",
                ],
                "patch_diff": "--- a/src/core/config.py\n+++ b/src/core/config.py\n@@ -22,3 +22,3 @@\n-    db_pool_size: int = 10\n-    db_max_overflow: int = 5\n+    db_pool_size: int = 30\n+    db_max_overflow: int = 10",
                "rollback_plan": "kubectl rollout restart deployment pgbouncer",
                "justification": "Encerrar conexões ociosas e reiniciar pod libera imediatamente os slots para novas requisições.",
                "tier_1_runtime": {
                    "action_type": "DATABASE_CONNECTION_SCALE",
                    "target_endpoint": "https://chaos-lab-197215016090.us-central1.run.app/operations/mitigate",
                    "proposed_commands": [
                        "POST /operations/mitigate action_type=DATABASE_CONNECTION_SCALE",
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';",
                    ],
                    "rollback_plan": "Restaurar max_connections original",
                },
                "tier_2_gitops": {
                    "target_repo": "henriquebotelhogomes/chaos-lab",
                    "target_branch": "main",
                    "pr_branch_name": "fix/opsmesh-conn-leak-8f3a",
                    "pr_title": "fix(db): expand connection pool capacity from 10 to 30",
                    "pr_body": "## Diagnóstico da Causa Raiz\nSaturação do pool de conexões (15/10) sob alto tráfego.\n\n## Solução Definitiva\nExpande pool_size para 30 e max_overflow para 10 no arquivo `src/core/config.py`.",
                    "patch_diff": "--- a/src/core/config.py\n+++ b/src/core/config.py\n@@ -22,3 +22,3 @@\n-    db_pool_size: int = 10\n-    db_max_overflow: int = 5\n+    db_pool_size: int = 30\n+    db_max_overflow: int = 10",
                },
            },

            "retrieved_sources": ["connection_pool.md"],
            "total_tokens_consumed": 0,
            "is_budget_exceeded": False,
            "agent_results": {
                "LogTraceAnalystAgent": {
                    "error_spike_percentage": 85.0,
                    "probable_origin_service": "order-service",
                    "summary": "Detectado pico anômalo de 85% em erros de aquisição de conexão (ConnectionPoolTimeoutException). O serviço 'order-service' reteve 98 conexões abertas sem fechar cursores.",
                    "found_anomalies": [
                        {
                            "error_pattern": "org.postgresql.util.PSQLException: FATAL: remaining connection slots are reserved",
                            "frequency": 142,
                            "first_seen": "2026-09-10T00:01:12Z",
                            "last_seen": "2026-09-10T00:11:45Z",
                            "sample_message": "FATAL: remaining connection slots are reserved for non-replication superuser connections (client=10.244.2.15)",
                        },
                        {
                            "error_pattern": "HikariPool-1 - Connection is not available, request timed out after 30000ms",
                            "frequency": 89,
                            "first_seen": "2026-09-10T00:02:04Z",
                            "last_seen": "2026-09-10T00:11:30Z",
                            "sample_message": "HikariPool-1 - Connection is not available, request timed out after 30000ms at checkout_flow()",
                        },
                    ],
                },
                "DatabaseInfraAgent": {
                    "database_pool_utilization_pct": 98.0,
                    "active_long_running_queries": 47,
                    "pod_restart_count": 0,
                    "is_resource_exhausted": True,
                    "diagnostic_evidence": "pg_stat_activity aponta 98 de 100 conexões alocadas; 47 sessões em estado 'idle in transaction' há mais de 12 minutos originadas de order-service.",
                },
                "RunbookKnowledgeAgent": {
                    "synthesis": "Procedimento primário recomendado: [SOP-DB-002] Saturação do Pool de Conexões Postgres.",
                    "recommendations": [
                        {
                            "runbook_title": "SOP-DB-002: Saturação de Conexões PostgreSQL",
                            "section": "Procedimento Emergencial de Purga de Conexões Ociosas",
                            "recommended_procedure": "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND state_change < current_timestamp - INTERVAL '5 minutes';",
                            "source_file": "connection_pool.md",
                            "confidence_score": 0.96,
                        },
                    ],
                },
            },
        },
    ),
    "checkout-timeout": ChaosScenario(
        id="checkout-timeout",
        title="Timeout em Cascata e HTTP 504 no Checkout",
        description="Lentidão extrema no serviço de inventário causa timeout na API de checkout durante compra.",
        severity="P0_CRITICAL",
        service="checkout-api",
        expected_root_cause="Upstream inventory-service timeout causing HTTP 504 cascades",
        alert_payload={
            "service": "checkout-api",
            "message": "GatewayTimeout: Upstream inventory-service timed out after 3000ms at /api/v1/stock/reserve",
            "severity": "P0_CRITICAL",
            "source": "prometheus",
            "details": {"error_rate_5xx": "24.2%", "p99_latency_ms": 8400},
        },
        cached_replay_response={
            "incident_id": "INC-REPLAY-CHK-02",
            "severity": "P0_CRITICAL",
            "status": "AWAITING_APPROVAL",
            "root_cause_summary": "Lentidão crítica e esgotamento de threads no microsserviço de inventário gerando HTTP 504 em cascata no checkout.",
            "remediation_plan": {
                "action_type": "CIRCUIT_BREAKER_ACTIVATE",
                "is_critical_action": True,
                "risk_level": "MEDIUM",
                "proposed_commands": [
                    "POST /operations/mitigate (target_action: CIRCUIT_BREAKER_ACTIVATE)",
                    "kubectl scale deployment chaos-lab --replicas=3 -n production",
                ],
                "patch_diff": "--- a/src/core/config.py\n+++ b/src/core/config.py\n@@ -24,2 +24,3 @@\n-    db_timeout_seconds: float = 3.0\n+    db_timeout_seconds: float = 5.0\n+    inventory_circuit_breaker: bool = True",
                "rollback_plan": "Fechar circuit breaker quando a latência normalizar abaixo de 200ms.",
                "justification": "Ativar fallback assíncrono evita perda direta de vendas no checkout.",
                "tier_1_runtime": {
                    "action_type": "CIRCUIT_BREAKER_ACTIVATE",
                    "target_endpoint": "https://chaos-lab-197215016090.us-central1.run.app/operations/mitigate",
                    "proposed_commands": [
                        "POST /operations/mitigate action_type=CIRCUIT_BREAKER_ACTIVATE",
                    ],
                    "rollback_plan": "Desativar circuit breaker",
                },
                "tier_2_gitops": {
                    "target_repo": "henriquebotelhogomes/chaos-lab",
                    "target_branch": "main",
                    "pr_branch_name": "fix/opsmesh-inventory-timeout",
                    "pr_title": "fix(inventory): add circuit breaker and increase timeout tolerance",
                    "pr_body": "## Diagnóstico da Causa Raiz\nTimeout em cascata downstream estourando 504 no checkout.\n\n## Solução Definitiva\nAjusta timeout e habilita circuit breaker em `src/core/config.py`.",
                    "patch_diff": "--- a/src/core/config.py\n+++ b/src/core/config.py\n@@ -24,2 +24,3 @@\n-    db_timeout_seconds: float = 3.0\n+    db_timeout_seconds: float = 5.0\n+    inventory_circuit_breaker: bool = True",
                },
            },

            "retrieved_sources": ["checkout_timeout.md"],
            "total_tokens_consumed": 0,
            "is_budget_exceeded": False,
            "agent_results": {
                "LogTraceAnalystAgent": {
                    "error_spike_percentage": 78.0,
                    "probable_origin_service": "checkout-api",
                    "summary": "Pico de 78% em erros HTTP 504 Gateway Timeout no endpoint /api/v1/stock/reserve. Cascade de bloqueio de threads síncronas.",
                    "found_anomalies": [
                        {
                            "error_pattern": "GatewayTimeout: Upstream inventory-service timed out after 3000ms",
                            "frequency": 215,
                            "first_seen": "2026-09-10T00:04:10Z",
                            "last_seen": "2026-09-10T00:11:50Z",
                            "sample_message": "GatewayTimeout: Upstream inventory-service timed out after 3000ms at /api/v1/stock/reserve",
                        },
                    ],
                },
                "DatabaseInfraAgent": {
                    "database_pool_utilization_pct": 34.0,
                    "active_long_running_queries": 2,
                    "pod_restart_count": 0,
                    "is_resource_exhausted": False,
                    "diagnostic_evidence": "Pods de checkout-api com 100% de CPU throttling por saturação de threads aguardando resposta síncrona de inventory-service.",
                },
                "RunbookKnowledgeAgent": {
                    "synthesis": "Procedimento primário recomendado: [SOP-API-001] Falha em Cascata e Ativação de Circuit Breaker.",
                    "recommendations": [
                        {
                            "runbook_title": "SOP-API-001: Ativação de Circuit Breaker em Cascata",
                            "section": "Degradação Graciosa de Checkout",
                            "recommended_procedure": "Ativar flag 'inventory_fallback_enabled': true para enviar reservas de estoque para fila assíncrona RabbitMQ/SQS temporariamente.",
                            "source_file": "checkout_timeout.md",
                            "confidence_score": 0.94,
                        },
                    ],
                },
            },
        },
    ),
    "payment-latency": ChaosScenario(
        id="payment-latency",
        title="Degradação e Latência no Gateway de Pagamentos",
        description="Spike de latência externa no adquirente e acúmulo de webhooks na fila.",
        severity="P1_HIGH",
        service="payment-worker",
        expected_root_cause="External payment gateway latency spike p99 > 12s",
        alert_payload={
            "service": "payment-worker",
            "message": "External payment gateway latency spike: p99 reached 12.4s (threshold: 2.0s) with connection timeouts",
            "severity": "P1_HIGH",
            "source": "grafana",
            "details": {"pending_webhooks": 1420},
        },
        cached_replay_response={
            "incident_id": "INC-REPLAY-PAY-03",
            "severity": "P1_HIGH",
            "status": "AWAITING_APPROVAL",
            "root_cause_summary": "Latência externa extrema no adquirente de pagamentos causando timeout e represamento de fila.",
            "remediation_plan": {
                "action_type": "TRAFFIC_DRAIN",
                "is_critical_action": True,
                "risk_level": "HIGH",
                "proposed_commands": [
                    "POST /operations/mitigate (target_action: CIRCUIT_BREAKER_ACTIVATE)",
                    "Comutar para adquirente secundário (Stripe -> Adyen)",
                ],
                "patch_diff": "--- a/src/api/routes.py\n+++ b/src/api/routes.py\n@@ -131,2 +131,4 @@\n-        raise HTTPException(status_code=502, detail=\"Bad Gateway\")\n+        # Failover com retry exponencial\n+        return await process_secondary_payment(payload)",
                "rollback_plan": "Recomutar para o adquirente primário após confirmação de normalização do SLA externo.",
                "justification": "Comutar para o gateway secundário desrepresa imediatamente as transações pendentes.",
                "tier_1_runtime": {
                    "action_type": "CIRCUIT_BREAKER_ACTIVATE",
                    "target_endpoint": "https://chaos-lab-197215016090.us-central1.run.app/operations/mitigate",
                    "proposed_commands": [
                        "POST /operations/mitigate action_type=CIRCUIT_BREAKER_ACTIVATE",
                    ],
                    "rollback_plan": "Restaurar rota primária",
                },
                "tier_2_gitops": {
                    "target_repo": "henriquebotelhogomes/chaos-lab",
                    "target_branch": "main",
                    "pr_branch_name": "fix/opsmesh-stripe-failover",
                    "pr_title": "fix(payment): implement secondary payment processor failover",
                    "pr_body": "## Diagnóstico da Causa Raiz\nOscilação externa e timeouts no gateway primário.\n\n## Solução Definitiva\nAdiciona fallback resiliente no arquivo `src/api/routes.py`.",
                    "patch_diff": "--- a/src/api/routes.py\n+++ b/src/api/routes.py\n@@ -131,2 +131,4 @@\n-        raise HTTPException(status_code=502, detail=\"Bad Gateway\")\n+        # Failover com retry exponencial\n+        return await process_secondary_payment(payload)",
                },
            },
            "retrieved_sources": ["payment_latency.md"],
            "total_tokens_consumed": 0,
            "is_budget_exceeded": False,
            "agent_results": {
                "LogTraceAnalystAgent": {
                    "error_spike_percentage": 65.0,
                    "probable_origin_service": "payment-worker",
                    "summary": "Latência p99 saltou para 12.4s no gateway adquirente externo. 1420 webhooks enfileirados aguardando processamento com timeout.",
                    "found_anomalies": [
                        {
                            "error_pattern": "ConnectionTimeout: Acquirer API did not respond within 10000ms",
                            "frequency": 164,
                            "first_seen": "2026-09-10T00:02:40Z",
                            "last_seen": "2026-09-10T00:11:15Z",
                            "sample_message": "ConnectionTimeout: Acquirer API https://api.primary-gateway.internal did not respond within 10000ms",
                        },
                    ],
                },
                "DatabaseInfraAgent": {
                    "database_pool_utilization_pct": 28.0,
                    "active_long_running_queries": 0,
                    "pod_restart_count": 0,
                    "is_resource_exhausted": False,
                    "diagnostic_evidence": "Fila Redis/RabbitMQ de pagamentos com 1.420 mensagens acumuladas devido à latência de resposta do adquirente externo.",
                },
                "RunbookKnowledgeAgent": {
                    "synthesis": "Procedimento primário recomendado: [SOP-PAY-003] Dreno e Comutação Automática de Gateway de Pagamento.",
                    "recommendations": [
                        {
                            "runbook_title": "SOP-PAY-003: Failover de Gateway de Pagamento",
                            "section": "Comutação Dinâmica de Adquirente",
                            "recommended_procedure": "Comutar tráfego de autorização de cartão para adquirente secundário via POST /v1/payments/gateway-switch target=SECONDARY_STONE.",
                            "source_file": "payment_latency.md",
                            "confidence_score": 0.98,
                        },
                    ],
                },
            },
        },
    ),
    "model-drift-oom": ChaosScenario(
        id="model-drift-oom",
        title="Vazamento de Memória e Pods OOMKilled no Recommendation Engine",
        description="Versão canary de modelo ML vaza tensores em memória, causando CrashLoopBackOff repetido.",
        severity="P1_HIGH",
        service="recommendation-ml",
        expected_root_cause="Tensor memory leak in v1.5.0 causing container exit code 137 (OOMKilled)",
        alert_payload={
            "service": "recommendation-ml",
            "message": "Container recommendation-engine terminated with exitCode 137 (OOMKilled) on node worker-03",
            "severity": "P1_HIGH",
            "source": "datadog",
            "details": {"exit_code": 137, "restarts": 9},
        },
        cached_replay_response={
            "incident_id": "INC-REPLAY-ML-04",
            "severity": "P1_HIGH",
            "status": "AWAITING_APPROVAL",
            "root_cause_summary": "Vazamento contínuo de memória em processo de inferência Python levando a término forçado pelo Kubelet (Exit Code 137 - OOMKilled).",
            "remediation_plan": {
                "action_type": "CONFIG_ROLLBACK",
                "is_critical_action": True,
                "risk_level": "CRITICAL",
                "proposed_commands": [
                    "POST /operations/mitigate (target_action: FLUSH_GC)",
                    "Reiniciar pods e forçar coleta de lixo no runtime",
                ],
                "patch_diff": "--- a/src/chaos/state.py\n+++ b/src/chaos/state.py\n@@ -38,2 +38,4 @@\n-    def inject_memory_leak(self, megabytes=25):\n-        self.leaked_chunks.append(bytearray(megabytes * 1024 * 1024))\n+    def inject_memory_leak(self, megabytes=25):\n+        # Coleta de lixo forçada e buffer limitado\n+        import gc; gc.collect()",
                "rollback_plan": "Reverter para pod shadow de contingência caso ocorra divergência.",
                "justification": "Rollback e liberação de tensores elimina o vazamento de memória imediatamente.",
                "tier_1_runtime": {
                    "action_type": "FLUSH_GC",
                    "target_endpoint": "https://chaos-lab-197215016090.us-central1.run.app/operations/mitigate",
                    "proposed_commands": [
                        "POST /operations/mitigate action_type=FLUSH_GC",
                    ],
                    "rollback_plan": "Restaurar estado anterior",
                },
                "tier_2_gitops": {
                    "target_repo": "henriquebotelhogomes/chaos-lab",
                    "target_branch": "main",
                    "pr_branch_name": "fix/opsmesh-gc-memory-cleanup",
                    "pr_title": "fix(memory): force garbage collection and limit chunk buffer allocations",
                    "pr_body": "## Diagnóstico da Causa Raiz\nVazamento de tensores de memória acumulando no Garbage Collector.\n\n## Solução Definitiva\nAplica desalocação forçada e cleanup em `src/chaos/state.py`.",
                    "patch_diff": "--- a/src/chaos/state.py\n+++ b/src/chaos/state.py\n@@ -38,2 +38,4 @@\n-    def inject_memory_leak(self, megabytes=25):\n-        self.leaked_chunks.append(bytearray(megabytes * 1024 * 1024))\n+    def inject_memory_leak(self, megabytes=25):\n+        # Coleta de lixo forçada e buffer limitado\n+        import gc; gc.collect()",
                },
            },

            "retrieved_sources": ["model_drift_oom.md"],
            "total_tokens_consumed": 0,
            "is_budget_exceeded": False,
            "agent_results": {
                "LogTraceAnalystAgent": {
                    "error_spike_percentage": 92.0,
                    "probable_origin_service": "recommendation-ml",
                    "summary": "Container recommendation-engine falha repetidamente com exitCode 137 (OOMKilled) por vazamento contínuo de memória em tensores PyTorch.",
                    "found_anomalies": [
                        {
                            "error_pattern": "Kubelet: Container recommendation-engine exceeded memory limit (8GiB) and was killed",
                            "frequency": 9,
                            "first_seen": "2026-09-10T00:01:00Z",
                            "last_seen": "2026-09-10T00:10:30Z",
                            "sample_message": "OOMKilled: Process 1241 (python inference.py) invoked oom-killer: gfp_mask=0x1100cca, order=0, oom_score_adj=998",
                        },
                    ],
                },
                "DatabaseInfraAgent": {
                    "database_pool_utilization_pct": 15.0,
                    "active_long_running_queries": 0,
                    "pod_restart_count": 9,
                    "is_resource_exhausted": True,
                    "diagnostic_evidence": "Pods do deployment recommendation-ml em CrashLoopBackOff. Consumo de RAM atingiu 8.1 GiB (limite K8s: 8.0 GiB) após rollout da versão v1.5.0-canary.",
                },
                "RunbookKnowledgeAgent": {
                    "synthesis": "Procedimento primário recomendado: [SOP-ML-004] Rollback Imediato de Imagem em Caso de Vazamento de Memória.",
                    "recommendations": [
                        {
                            "runbook_title": "SOP-ML-004: Rollback de Modelos de Inferência",
                            "section": "Reversão de Canary com OOM",
                            "recommended_procedure": "kubectl set image deployment/recommendation-ml worker=registry.internal/ml/recommendation:v1.4.2-stable -n production && kubectl rollout status deployment/recommendation-ml",
                            "source_file": "model_drift_oom.md",
                            "confidence_score": 0.97,
                        },
                    ],
                },
            },
        },
    ),
}


class ChaosStudio:
    """Chaos Engineering Studio with Zero-Token Replay Sandbox."""

    @staticmethod
    def list_scenarios() -> list[dict[str, Any]]:
        """Return metadata for all 4 canonical crisis scenarios."""
        return [
            {
                "id": s.id,
                "title": s.title,
                "description": s.description,
                "severity": s.severity,
                "service": s.service,
                "expected_root_cause": s.expected_root_cause,
            }
            for s in SCENARIOS.values()
        ]

    @staticmethod
    def get_scenario(scenario_id: str) -> ChaosScenario | None:
        """Get scenario details by id."""
        return SCENARIOS.get(scenario_id)

    @classmethod
    async def simulate_scenario(
        cls,
        scenario_id: str,
        demo_mode: str = "replay",
        graph_app: Any = None,
    ) -> IncidentResponse:
        """Simulate crisis scenario in Zero-Token Replay mode or Live execution mode."""
        scenario = SCENARIOS.get(scenario_id)
        if not scenario:
            raise ValueError(f"Cenário de caos '{scenario_id}' não encontrado.")

        # Zero-Token Replay Mode: instant response from cached telemetry
        if demo_mode == "replay" or graph_app is None:
            cached = scenario.cached_replay_response
            return IncidentResponse(
                incident_id=f"{cached['incident_id']}-{uuid.uuid4().hex[:4].upper()}",
                severity=cached["severity"],
                status=cached["status"],
                root_cause_summary=cached["root_cause_summary"],
                remediation_plan=cached["remediation_plan"],
                retrieved_sources=cached.get("retrieved_sources", []),
                total_tokens_consumed=0,  # Zero-Token guarantee
                is_budget_exceeded=False,
                agent_results=cached.get("agent_results", {}),
            )

        # Live Execution Mode
        incident_id = f"INC-CHAOS-{uuid.uuid4().hex[:8].upper()}"
        thread_id = f"thread-{incident_id}"
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "incident_id": incident_id,
            "severity": scenario.severity,
            "status": "INVESTIGATING",
            "raw_alert_sanitized": scenario.alert_payload,
            "messages": [],
            "agent_results": {},
            "retrieved_sources": [],
            "root_cause_summary": None,
            "remediation_plan": None,
            "error_message": None,
            "human_approved": None,
            "approved_by": None,
            "approval_timestamp": None,
            "iteration_count": 1,
            "max_iterations": 4,
            "token_budget_limit": 12000,
            "total_tokens_consumed": 150,
            "is_budget_exceeded": False,
            "trace_id": f"trace-{incident_id}",
            "langsmith_run_id": None,
        }

        await graph_app.ainvoke(initial_state, config=config)
        snapshot = await graph_app.aget_state(config)
        values = snapshot.values

        return IncidentResponse(
            incident_id=incident_id,
            severity=values.get("severity", scenario.severity),
            status=values.get("status", "AWAITING_APPROVAL"),
            root_cause_summary=values.get("root_cause_summary"),
            remediation_plan=values.get("remediation_plan"),
            retrieved_sources=values.get("retrieved_sources", []),
            total_tokens_consumed=values.get("total_tokens_consumed", 150),
            is_budget_exceeded=values.get("is_budget_exceeded", False),
            agent_results=values.get("agent_results", {}),
        )
