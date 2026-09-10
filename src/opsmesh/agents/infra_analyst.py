"""DatabaseInfraAgent.

Specialist agent inspecting database saturation, active locks, and Kubernetes
deployment health with strict read-only guarantees (least-privilege).
"""

from __future__ import annotations

import json
import logging

from opsmesh.core.schemas import InfraAnalysisResult
from opsmesh.gateway.dispatcher import ToolDispatcher

logger = logging.getLogger(__name__)


class DatabaseInfraAgent:
    """Specialist agent for database and infrastructure diagnostics."""

    def __init__(self, dispatcher: ToolDispatcher | None = None) -> None:
        self.dispatcher = dispatcher or ToolDispatcher()

    async def analyze(self, directive: str) -> InfraAnalysisResult:
        """Inspect database and container infrastructure state."""
        # 1. Query database activity
        db_raw = await self.dispatcher.execute_tool(
            "inspect_database_activity",
            {
                "metric": "connections"
                if "conn" in directive.lower() or "pool" in directive.lower()
                else "locks"
            },
        )

        # 2. Query Kubernetes deployment health
        service_hint = (
            "recommendation-ml"
            if (
                "ml" in directive.lower()
                or "oom" in directive.lower()
                or "mem" in directive.lower()
            )
            else "order-service"
        )
        k8s_raw = await self.dispatcher.execute_tool(
            "check_k8s_deployment_health", {"service_name": service_hint}
        )

        pool_pct = 0.0
        slow_queries = 0
        restart_count = 0
        exhausted = False
        evidence_parts = []

        try:
            db_data = json.loads(db_raw)
            if isinstance(db_data, dict):
                pool_pct = float(db_data.get("connection_pool_utilization_pct", 0.0))
                slow_queries = int(
                    db_data.get("waiting_connections", 0) or db_data.get("blocked_queries_count", 0)
                )
                if pool_pct >= 90.0 or db_data.get("status") == "CRITICAL_SATURATION":
                    exhausted = True
                    evidence_parts.append(
                        f"PostgreSQL com {pool_pct}% de utilização do pool e {slow_queries} conexões em espera."
                    )
        except Exception:
            evidence_parts.append("Não foi possível parsear métricas do PostgreSQL.")

        try:
            k8s_data = json.loads(k8s_raw)
            if isinstance(k8s_data, dict):
                pods = k8s_data.get("pods", [])
                restart_count = sum(p.get("restart_count", 0) for p in pods if isinstance(p, dict))
                if restart_count > 0:
                    exhausted = True
                    evidence_parts.append(
                        f"Kubernetes reporta {restart_count} reinícios em pods com eventos: {k8s_data.get('events', [])}"
                    )
        except Exception:
            evidence_parts.append("Não foi possível parsear métricas do Kubernetes.")

        return InfraAnalysisResult(
            database_pool_utilization_pct=pool_pct,
            active_long_running_queries=slow_queries,
            pod_restart_count=restart_count,
            is_resource_exhausted=exhausted,
            diagnostic_evidence=" | ".join(evidence_parts)
            or "Infraestrutura operacional dentro dos limites nominais.",
        )
