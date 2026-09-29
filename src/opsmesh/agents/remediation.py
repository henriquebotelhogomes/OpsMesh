"""RemediationEngineerAgent.

Formulates safe, idempotent mitigation plans, generates config/patch diffs,
defines rollback strategies, and enforces strict Human-in-the-Loop gating.
"""

from __future__ import annotations

import logging
from typing import Any

from opsmesh.core.schemas import GitOpsPullRequest, RemediationPlan, RuntimeMitigation

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
            patch = """--- a/helm/order-service/values.yaml
+++ b/helm/order-service/values.yaml
@@ -14,3 +14,3 @@ database:
-  pool_max_size: 20
-  pool_timeout_seconds: 5.0
+  pool_max_size: 50
+  pool_timeout_seconds: 15.0"""
            return RemediationPlan(
                action_type="DATABASE_TERMINATE_BACKENDS",
                is_critical_action=True,
                risk_level="HIGH",
                proposed_commands=[
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND now() - query_start > interval '120 seconds' AND usename != 'postgres';",
                    "kubectl rollout restart deployment order-service -n production",
                ],
                patch_diff=patch,
                rollback_plan="Caso a terminação das conexões afete transações ativas, reverter a escala do pool e reiniciar PgBouncer: kubectl rollout restart deployment pgbouncer.",
                justification="Existem dezenas de conexões presas em 'idle in transaction' saturando o pool em 98%. Encerrar as conexões ociosas e reiniciar o pod libera imediatamente os slots para novas requisições.",
                tier_1_runtime=RuntimeMitigation(
                    action_type="DATABASE_TERMINATE_BACKENDS",
                    target_endpoint="POST /operations/mitigate",
                    proposed_commands=[
                        "POST /operations/mitigate (target: postgres-pool)",
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction';",
                    ],
                    rollback_plan="kubectl rollout restart deployment pgbouncer",
                ),
                tier_2_gitops=GitOpsPullRequest(
                    target_repo="henriquebotelhogomes/chaos-lab",
                    target_branch="main",
                    pr_branch_name="fix/opsmesh-postgres-pool-expansion",
                    pr_title="fix(db): expand connection pool and add query timeout",
                    pr_body=(
                        "## Diagnóstico da Causa Raiz\n"
                        "Pool de conexões exaurido por conexões ociosas.\n\n"
                        "## Mudanças Propostas\n"
                        "- Aumento de `pool_max_size` de 20 para 50.\n"
                        "- Aumento de timeout de 5.0s para 15.0s.\n\n"
                        "*Gerado automaticamente pelo OpsMesh Incident Commander.*"
                    ),
                    patch_diff=patch,
                ),
            )

        # Scenario 2: Model Drift / Memory Leak / OOMKilled
        elif (
            "oom" in summary
            or "memory" in summary
            or "drift" in summary
            or "exitcode 137" in summary
            or "137" in alert_text
        ):
            patch = """--- a/k8s/recommendation-deployment.yaml
+++ b/k8s/recommendation-deployment.yaml
@@ -21,3 +21,3 @@ spec:
-      - image: registry.internal/ml/recommendation:v1.5.0-canary
+      - image: registry.internal/ml/recommendation:v1.4.2-stable
         resources:
           limits:
-            memory: "4Gi"
+            memory: "8Gi" """
            return RemediationPlan(
                action_type="CONFIG_ROLLBACK",
                is_critical_action=True,
                risk_level="CRITICAL",
                proposed_commands=[
                    "kubectl set image deployment/recommendation-ml worker=registry.internal/ml/recommendation:v1.4.2 -n production",
                    "kubectl rollout status deployment/recommendation-ml -n production --timeout=180s",
                ],
                patch_diff=patch,
                rollback_plan="Se a versão v1.4.2 apresentar incompatibilidade de payload, comutar o tráfego para a réplica de contingência em modo shadow.",
                justification="A versão canary v1.5.0 possui vazamento contínuo de tensores em memória, causando OOMKilled repetido (exit 137) nos pods. O rollback restaura a estabilidade.",
                tier_1_runtime=RuntimeMitigation(
                    action_type="CONFIG_ROLLBACK",
                    target_endpoint="POST /operations/mitigate",
                    proposed_commands=[
                        "POST /operations/mitigate (target: memory-leak)",
                        "kubectl rollout restart deployment recommendation-ml -n production",
                    ],
                    rollback_plan="kubectl rollout undo deployment recommendation-ml -n production",
                ),
                tier_2_gitops=GitOpsPullRequest(
                    target_repo="henriquebotelhogomes/chaos-lab",
                    target_branch="main",
                    pr_branch_name="fix/opsmesh-ml-canary-rollback",
                    pr_title="fix(ml): rollback canary model to v1.4.2-stable",
                    pr_body=(
                        "## Diagnóstico da Causa Raiz\n"
                        "Vazamento de tensores de memória causando OOMKilled repetido.\n\n"
                        "## Mudanças Propostas\n"
                        "- Reversão para imagem estável v1.4.2.\n"
                        "- Ajuste de limite de memória para 8Gi.\n\n"
                        "*Gerado automaticamente pelo OpsMesh Incident Commander.*"
                    ),
                    patch_diff=patch,
                ),
            )

        # Scenario 3: Checkout / Upstream Dependency Failure
        elif "checkout" in summary or "504" in summary or "timeout" in summary:
            patch = """--- a/config/checkout-service.json
+++ b/config/checkout-service.json
@@ -8,2 +8,2 @@
-  "inventory_fallback_enabled": false
+  "inventory_fallback_enabled": true"""
            return RemediationPlan(
                action_type="CIRCUIT_BREAKER_ACTIVATE",
                is_critical_action=True,
                risk_level="MEDIUM",
                proposed_commands=[
                    'curl -X POST http://consul.internal/v1/kv/config/checkout/inventory_circuit_breaker -d \'{"state": "OPEN", "fallback": "ASYNC_QUEUE"}\'',
                    "kubectl scale deployment inventory-service --replicas=6 -n production",
                ],
                patch_diff=patch,
                rollback_plan="Fechar o disjuntor de circuito assim que a latência do microsserviço de inventário normalizar abaixo de 200ms.",
                justification="O microsserviço de inventário está em cascata de timeouts. Abrir o circuit breaker com fallback assíncrono evita perda de vendas no checkout.",
                tier_1_runtime=RuntimeMitigation(
                    action_type="CIRCUIT_BREAKER_ACTIVATE",
                    target_endpoint="POST /operations/mitigate",
                    proposed_commands=[
                        "POST /operations/mitigate (target: timeout)",
                        'curl -X POST http://consul.internal/v1/kv/config/checkout/circuit_breaker -d \'{"state": "OPEN"}\'',
                    ],
                    rollback_plan='curl -X POST http://consul.internal/v1/kv/config/checkout/circuit_breaker -d \'{"state": "CLOSED"}\'',
                ),
                tier_2_gitops=GitOpsPullRequest(
                    target_repo="henriquebotelhogomes/chaos-lab",
                    target_branch="main",
                    pr_branch_name="fix/opsmesh-checkout-circuit-breaker",
                    pr_title="fix(checkout): enable inventory circuit breaker fallback",
                    pr_body=(
                        "## Diagnóstico da Causa Raiz\n"
                        "Cascata de timeouts HTTP 504 no checkout.\n\n"
                        "## Mudanças Propostas\n"
                        "- Ativação de fallback assíncrono para o inventário.\n\n"
                        "*Gerado automaticamente pelo OpsMesh Incident Commander.*"
                    ),
                    patch_diff=patch,
                ),
            )

        # Default Generic Safe Remediation
        default_patch = """--- a/deploy.yaml
+++ b/deploy.yaml
@@ -10,1 +10,1 @@
-  replicas: 1
+  replicas: 2"""
        return RemediationPlan(
            action_type="POD_ROLLOUT_RESTART",
            is_critical_action=True,
            risk_level="MEDIUM",
            proposed_commands=[
                "kubectl rollout restart deployment order-service -n production",
            ],
            patch_diff=default_patch,
            rollback_plan="kubectl rollout undo deployment order-service -n production",
            justification="Reiniciar de forma controlada as instâncias do serviço afetado para limpar eventuais threads bloqueadas ou conexões zumbis.",
            tier_1_runtime=RuntimeMitigation(
                action_type="POD_ROLLOUT_RESTART",
                target_endpoint="POST /operations/mitigate",
                proposed_commands=[
                    "kubectl rollout restart deployment order-service -n production"
                ],
                rollback_plan="kubectl rollout undo deployment order-service -n production",
            ),
            tier_2_gitops=GitOpsPullRequest(
                target_repo="henriquebotelhogomes/chaos-lab",
                target_branch="main",
                pr_branch_name="fix/opsmesh-service-stabilization",
                pr_title="chore(infra): automated service rollout stabilization",
                pr_body="Reinício controlado de pods para restabelecer estabilidade do serviço.",
                patch_diff=default_patch,
            ),
        )
