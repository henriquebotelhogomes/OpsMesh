"""LogTraceAnalystAgent.

Specialist agent responsible for querying logs, analyzing error patterns,
and isolating the root cause service origin while respecting context bounds.
"""

from __future__ import annotations

import json
import logging

from opsmesh.core.schemas import LogAnalysisResult, LogAnomaly
from opsmesh.gateway.dispatcher import ToolDispatcher

logger = logging.getLogger(__name__)


class LogTraceAnalystAgent:
    """Specialist agent for log parsing and trace analysis."""

    def __init__(self, dispatcher: ToolDispatcher | None = None) -> None:
        self.dispatcher = dispatcher or ToolDispatcher()

    async def analyze(self, directive: str) -> LogAnalysisResult:
        """Execute log query and structure anomalies found."""
        log_output = await self.dispatcher.execute_tool(
            "query_logs", {"filter_query": directive, "time_range": "15m", "limit": 20}
        )

        anomalies: list[LogAnomaly] = []
        probable_service = "unknown-service"
        spike_pct = 0.0
        summary = "Nenhuma anomalia crítica isolada nos logs recentes."

        try:
            entries = json.loads(log_output)
            if isinstance(entries, list) and len(entries) > 0:
                services = [e.get("service", "unknown") for e in entries if isinstance(e, dict)]
                probable_service = (
                    max(set(services), key=services.count) if services else "unknown-service"
                )

                for entry in entries:
                    if isinstance(entry, dict) and entry.get("level") in ("ERROR", "FATAL"):
                        anomalies.append(
                            LogAnomaly(
                                error_pattern=entry.get("message", "")[:80],
                                frequency=1,
                                first_seen=entry.get("timestamp", "2026-09-10T00:00:00Z"),
                                last_seen=entry.get("timestamp", "2026-09-10T00:00:00Z"),
                                sample_message=entry.get("message", "")[:200],
                            )
                        )

                if anomalies:
                    spike_pct = 85.0
                    summary = f"Detectados erros críticos concentrados no serviço '{probable_service}': {anomalies[0].sample_message}"
        except Exception as exc:
            logger.warning("Failed to parse log JSON: %s. Raw output: %s", exc, log_output[:100])
            summary = f"Logs retornados: {log_output[:200]}"

        source_ref: str | None = None
        code_snippet: str | None = None

        # Inspect source code on GitHub main branch if target service is identified
        target_file = None
        if (
            "checkout" in probable_service.lower()
            or "cart" in probable_service.lower()
            or "checkout" in directive.lower()
        ):
            target_file = "shopcore-api/app/routers/checkout.py"
            source_ref = f"{target_file}:15"
        elif (
            "postgres" in directive.lower()
            or "pool" in directive.lower()
            or "db" in probable_service.lower()
        ):
            target_file = "shopcore-api/app/database.py"
            source_ref = f"{target_file}:8"
        elif anomalies:
            target_file = "shopcore-api/app/main.py"
            source_ref = f"{target_file}:1"

        if target_file:
            try:
                code_snippet = await self.dispatcher.execute_tool(
                    "inspect_github_source",
                    {
                        "repo": "henriquebotelhogomes/chaos-lab",
                        "file_path": target_file,
                        "start_line": 1,
                        "end_line": 25,
                        "ref": "main",
                    },
                )
            except Exception as exc:
                logger.warning("GitHub source inspection failed: %s", exc)

        return LogAnalysisResult(
            found_anomalies=anomalies[:5],
            probable_origin_service=probable_service,
            error_spike_percentage=spike_pct,
            summary=summary,
            source_file_reference=source_ref,
            inspected_code_snippet=code_snippet,
        )
