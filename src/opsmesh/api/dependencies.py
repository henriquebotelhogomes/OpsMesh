"""API Dependencies, Rate Limiting & Graph Runtime Singleton."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from opsmesh.core.config import settings
from opsmesh.graph.builder import build_incident_graph

logger = logging.getLogger(__name__)

# Global rate limiter (5 req/min per IP as per FinOps protection)
limiter = Limiter(
    key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)

_graph_app: Any = None
_incident_registry: dict[str, dict[str, Any]] = {}


def _seed_registry_history() -> None:
    """Seed registry with canonical past resolved incidents for audit history and portfolio demo."""
    from opsmesh.chaos.studio import SCENARIOS

    scen_map = [
        (
            "postgres-pool",
            "INC-HIST-POOL-01",
            "order-service",
            "RESOLVED",
            True,
            "sre-lead@enterprise.org",
            "2026-09-09T22:30:15Z",
            "2026-09-09T22:15:00Z",
        ),
        (
            "checkout-timeout",
            "INC-HIST-CHK-02",
            "checkout-api",
            "RESOLVED",
            True,
            "devops-oncall@enterprise.org",
            "2026-09-09T23:55:40Z",
            "2026-09-09T23:45:00Z",
        ),
        (
            "payment-latency",
            "INC-HIST-PAY-03",
            "payment-worker",
            "RESOLVED",
            True,
            "sre-commander@enterprise.org",
            "2026-09-10T00:14:22Z",
            "2026-09-10T00:02:10Z",
        ),
    ]

    for scen_id, inc_id, svc, st, approved, approver, approved_at, created_at in scen_map:
        scen = SCENARIOS.get(scen_id)
        if not scen:
            continue
        cached = scen.cached_replay_response
        _incident_registry[inc_id] = {
            "thread_id": f"thread-{inc_id}",
            "is_replay": True,
            "values": {
                **cached,
                "incident_id": inc_id,
                "status": st,
                "service": svc,
                "created_at": created_at,
                "human_approved": approved,
                "approved_by": approver,
                "approval_timestamp": approved_at,
            },
        }


async def get_graph_app() -> Any:
    """Retrieve or lazily initialize the compiled LangGraph workflow."""
    global _graph_app
    if _graph_app is None:
        _graph_app = await build_incident_graph()
    return _graph_app


def get_incident_registry() -> dict[str, dict[str, Any]]:
    """In-memory metadata registry for fast lookup of active incidents and audit history."""
    if not _incident_registry:
        _seed_registry_history()
    return _incident_registry


def extract_byok_keys(request: Request) -> dict[str, str]:
    """Extract BYOK (Bring Your Own Key) headers if provided by user."""
    keys = {}
    openai_key = request.headers.get("X-OpenAI-API-Key")
    deepseek_key = request.headers.get("X-DeepSeek-API-Key")

    if openai_key:
        keys["openai"] = openai_key
    if deepseek_key:
        keys["deepseek"] = deepseek_key
    return keys
