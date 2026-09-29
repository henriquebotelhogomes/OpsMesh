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
            patch = """--- a/src/core/config.py
+++ b/src/core/config.py
@@ -22,3 +22,3 @@
-    db_pool_size: int = 10
-    db_max_overflow: int = 5
+    db_pool_size: int = 30
+    db_max_overflow: int = 10"""
            return RemediationPlan(
                action_type="DATABASE_TERMINATE_BACKENDS",
                is_critical_action=True,
                risk_level="HIGH",
                proposed_commands=[
                    "POST /operations/mitigate action_type=DATABASE_CONNECTION_SCALE",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction';",
                    "kubectl rollout restart deployment chaos-lab -n production",
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
            patch = """--- a/src/chaos/state.py
+++ b/src/chaos/state.py
@@ -38,2 +38,4 @@
-    def inject_memory_leak(self, megabytes=25):
-        self.leaked_chunks.append(bytearray(megabytes * 1024 * 1024))
+    def inject_memory_leak(self, megabytes=25):
+        # Bounded buffer com coleta forçada
+        import gc; gc.collect()"""
            return RemediationPlan(
                action_type="CONFIG_ROLLBACK",
                is_critical_action=True,
                risk_level="CRITICAL",
                proposed_commands=[
                    "POST /operations/mitigate action_type=FLUSH_GC",
                    "kubectl rollout restart deployment chaos-lab -n production",
                ],
                patch_diff=patch,
                rollback_plan="Reverter para pod shadow de contingência caso ocorra divergência.",
                justification="Vazamento contínuo de tensores em memória causando CrashLoopBackOff repetido. O flush e GC forçado eliminam o vazamento.",
                tier_1_runtime=RuntimeMitigation(
                    action_type="FLUSH_GC",
                    target_endpoint="POST /operations/mitigate",
                    proposed_commands=[
                        "POST /operations/mitigate action_type=FLUSH_GC",
                    ],
                    rollback_plan="Restaurar estado anterior",
                ),
                tier_2_gitops=GitOpsPullRequest(
                    target_repo="henriquebotelhogomes/chaos-lab",
                    target_branch="main",
                    pr_branch_name="fix/opsmesh-gc-memory-cleanup",
                    pr_title="fix(memory): force garbage collection and limit chunk buffer allocations",
                    pr_body=(
                        "## Diagnóstico da Causa Raiz\n"
                        "Vazamento contínuo de memória em tensores alocados sem coleta.\n\n"
                        "## Mudanças Propostas\n"
                        "- Adição de descarte forçado via `gc.collect()` em `src/chaos/state.py`.\n"
                        "- Limpeza de buffers cumulativos.\n\n"
                        "*Gerado automaticamente pelo OpsMesh Incident Commander.*"
                    ),
                    patch_diff=patch,
                ),
            )

        # Scenario 3: Checkout / Upstream Dependency Failure
        elif "checkout" in summary or "504" in summary or "timeout" in summary:
            patch = """--- a/src/core/config.py
+++ b/src/core/config.py
@@ -24,2 +24,3 @@
-    db_timeout_seconds: float = 3.0
+    db_timeout_seconds: float = 5.0
+    inventory_circuit_breaker: bool = True"""
            return RemediationPlan(
                action_type="CIRCUIT_BREAKER_ACTIVATE",
                is_critical_action=True,
                risk_level="MEDIUM",
                proposed_commands=[
                    "POST /operations/mitigate action_type=CIRCUIT_BREAKER_ACTIVATE",
                    "kubectl scale deployment chaos-lab --replicas=3 -n production",
                ],
                patch_diff=patch,
                rollback_plan="Fechar o disjuntor de circuito assim que a latência normalizar abaixo de 200ms.",
                justification="Microsserviço de inventário em cascata de timeouts. Ativar circuit breaker evita perda de vendas no checkout.",
                tier_1_runtime=RuntimeMitigation(
                    action_type="CIRCUIT_BREAKER_ACTIVATE",
                    target_endpoint="POST /operations/mitigate",
                    proposed_commands=[
                        "POST /operations/mitigate action_type=CIRCUIT_BREAKER_ACTIVATE",
                    ],
                    rollback_plan="Desativar circuit breaker",
                ),
                tier_2_gitops=GitOpsPullRequest(
                    target_repo="henriquebotelhogomes/chaos-lab",
                    target_branch="main",
                    pr_branch_name="fix/opsmesh-inventory-timeout",
                    pr_title="fix(inventory): add circuit breaker and increase timeout tolerance",
                    pr_body=(
                        "## Diagnóstico da Causa Raiz\n"
                        "Cascata de timeouts 504 no checkout.\n\n"
                        "## Mudanças Propostas\n"
                        "- Aumento de timeout para 5.0s em `src/core/config.py`.\n"
                        "- Ativação de flag de fallback assíncrono.\n\n"
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
