"""Chaos Studio & Replay REST Endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from opsmesh.api.dependencies import get_graph_app, get_incident_registry
from opsmesh.chaos.studio import ChaosStudio
from opsmesh.core.schemas import IncidentResponse

router = APIRouter(prefix="/api/v1/chaos", tags=["Chaos Studio & Sandbox"])


@router.get(
    "/scenarios",
    summary="Listar Cenários de Crise do Chaos Studio",
)
async def list_chaos_scenarios() -> list[dict[str, Any]]:
    """List the 4 canonical chaos crisis scenarios."""
    return ChaosStudio.list_scenarios()


@router.post(
    "/simulate/{scenario_id}",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Disparar Simulação de Crise (Modo Replay Zero-Token ou Live)",
)
async def simulate_crisis(
    scenario_id: str,
    mode: Literal["replay", "live"] = Query(
        default="replay",
        description="Modo de simulação: 'replay' (Zero-Token Sandbox, sem custos de API) ou 'live' (execução em tempo real).",
    ),
    model: str | None = Query(
        default=None,
        description="Modelo de LLM selecionado do OpenCode Go (ex: 'deepseek-v4.1-flash', 'glm-5.3-flash', 'gpt-5.6-luna', 'muse-spark-1.3-contributor').",
    ),
    graph_app: Any = Depends(get_graph_app),
    registry: dict = Depends(get_incident_registry),
) -> IncidentResponse:
    """Execute a chaos engineering crisis simulation."""
    try:
        response = await ChaosStudio.simulate_scenario(
            scenario_id=scenario_id,
            demo_mode=mode,
            graph_app=graph_app if mode == "live" else None,
        )

        scenario = ChaosStudio.get_scenario(scenario_id)
        service_name = scenario.service if scenario else "core-service"
        now_iso = datetime.now(UTC).isoformat()

        response.service = service_name
        response.created_at = now_iso

        # Store in registry so operator can query / resume
        registry[response.incident_id] = {
            "thread_id": f"thread-{response.incident_id}",
            "values": {
                **response.model_dump(),
                "service": service_name,
                "created_at": now_iso,
            },
            "is_replay": (mode == "replay"),
        }

        return response
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
