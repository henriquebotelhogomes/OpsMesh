"""RemediationEngineerAgent.

Formulates safe, idempotent mitigation plans, generates config/patch diffs,
defines rollback strategies, and enforces strict Human-in-the-Loop gating.
"""

from __future__ import annotations

import logging
from typing import Any

from opsmesh.core.schemas import RemediationPlan

logger = logging.getLogger(__name__)


class RemediationEngineerAgent:
    """Specialist agent formulating remediation and rollback plans."""

    async def plan(
        self,
        root_cause_summary: str | None,
        agent_results: dict[str, Any],
        raw_alert: dict[str, Any],
    ) -> RemediationPlan:
        """Formulate remediation plan based on consolidated diagnostics."""
        summary = (root_cause_summary or "").lower()
        alert_text = str(raw_alert).lower()

        # Scenario 1: Database Connection Pool Exhaustion
        if "postgres" in summary or "pool" in summary or "conn" in summary or "conn" in alert_text:
            return RemediationPlan(
                action_type="DATABASE_TERMINATE_BACKENDS",
                is_critical_action=True,
                risk_level="HIGH",
                proposed_commands=[
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND now() - query_start > interval '120 seconds' AND usename != 'postgres';",
                    "kubectl rollout restart deployment order-service -n production",
                ],
                patch_diff="""--- a/helm/order-service/values.yaml
+++ b/helm/order-service/values.yaml
@@ -14,3 +14,3 @@ database:
-  pool_max_size: 20
-  pool_timeout_seconds: 5.0
+  pool_max_size: 50
+  pool_timeout_seconds: 15.0""",
                rollback_plan="Caso a terminação das conexões afete transações ativas, reverter a escala do pool e reiniciar PgBouncer: kubectl rollout restart deployment pgbouncer.",
                justification="Existem dezenas de conexões presas em 'idle in transaction' saturando o pool em 98%. Encerrar as conexões ociosas e reiniciar o pod libera imediatamente os slots para novas requisições.",
            )

        # Scenario 2: Model Drift / Memory Leak / OOMKilled
        elif (
            "oom" in summary
            or "memory" in summary
            or "drift" in summary
            or "exitcode 137" in summary
            or "137" in alert_text
        ):
            return RemediationPlan(
                action_type="CONFIG_ROLLBACK",
                is_critical_action=True,
                risk_level="CRITICAL",
                proposed_commands=[
                    "kubectl set image deployment/recommendation-ml worker=registry.internal/ml/recommendation:v1.4.2 -n production",
                    "kubectl rollout status deployment/recommendation-ml -n production --timeout=180s",
                ],
                patch_diff="""--- a/k8s/recommendation-deployment.yaml
+++ b/k8s/recommendation-deployment.yaml
@@ -21,3 +21,3 @@ spec:
-      - image: registry.internal/ml/recommendation:v1.5.0-canary
+      - image: registry.internal/ml/recommendation:v1.4.2-stable
         resources:
           limits:
-            memory: "4Gi"
+            memory: "8Gi" """,
                rollback_plan="Se a versão v1.4.2 apresentar incompatibilidade de payload, comutar o tráfego para a réplica de contingência em modo shadow.",
                justification="A versão canary v1.5.0 possui vazamento contínuo de tensores em memória, causando OOMKilled repetido (exit 137) nos pods. O rollback restaura a estabilidade.",
            )

        # Scenario 3: Checkout / Upstream Dependency Failure
        elif "checkout" in summary or "504" in summary or "timeout" in summary:
            return RemediationPlan(
                action_type="CIRCUIT_BREAKER_ACTIVATE",
                is_critical_action=True,
                risk_level="MEDIUM",
                proposed_commands=[
                    'curl -X POST http://consul.internal/v1/kv/config/checkout/inventory_circuit_breaker -d \'{"state": "OPEN", "fallback": "ASYNC_QUEUE"}\'',
                    "kubectl scale deployment inventory-service --replicas=6 -n production",
                ],
                patch_diff="""--- a/config/checkout-service.json
+++ b/config/checkout-service.json
@@ -8,2 +8,2 @@
-  "inventory_fallback_enabled": false
+  "inventory_fallback_enabled": true""",
                rollback_plan="Fechar o disjuntor de circuito assim que a latência do microsserviço de inventário normalizar abaixo de 200ms.",
                justification="O microsserviço de inventário está em cascata de timeouts. Abrir o circuit breaker com fallback assíncrono evita perda de vendas no checkout.",
            )

        # Default Generic Safe Remediation
        return RemediationPlan(
            action_type="POD_ROLLOUT_RESTART",
            is_critical_action=True,
            risk_level="MEDIUM",
            proposed_commands=[
                "kubectl rollout restart deployment order-service -n production",
            ],
            patch_diff=None,
            rollback_plan="kubectl rollout undo deployment order-service -n production",
            justification="Reiniciar de forma controlada as instâncias do serviço afetado para limpar eventuais threads bloqueadas ou conexões zumbis.",
        )
