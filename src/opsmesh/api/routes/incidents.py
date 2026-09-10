"""Incident Management REST Endpoints.

Handles alert webhook ingestion, incident polling, Human-in-the-Loop approval/resume,
and immutable post-mortem report generation (JSON/PDF).
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from opsmesh.agents.post_mortem import AuditPostMortemAgent
from opsmesh.api.dependencies import (
    get_graph_app,
    get_incident_registry,
    limiter,
)
from opsmesh.core.config import settings
from opsmesh.core.pii_sanitizer import sanitize_pii
from opsmesh.core.schemas import (
    AlertPayload,
    IncidentResponse,
    PostMortemReport,
    ResumeIncidentRequest,
)
from opsmesh.core.state import IncidentState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/incidents", tags=["Incidents & HITL"])


@router.post(
    "/webhook",
    response_model=IncidentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingerir Alerta de Incidente (Datadog / Prometheus / Grafana)",
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def ingest_alert_webhook(
    request: Request,
    payload: AlertPayload,
    graph_app: Any = Depends(get_graph_app),
    registry: dict = Depends(get_incident_registry),
) -> IncidentResponse:
    """Ingest an incident alert, sanitize PII, and execute investigation up to HITL gate."""
    # 1. Sanitize PII with strict RFC 1918 preservation
    sanitized_alert = sanitize_pii(payload.model_dump(), preserve_rfc1918=True)

    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    thread_id = f"thread-{incident_id}"

    initial_state: IncidentState = {
        "incident_id": incident_id,
        "severity": payload.severity,
        "status": "INVESTIGATING",
        "raw_alert_sanitized": sanitized_alert,
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
        "max_iterations": settings.FINOPS_MAX_SUPERVISOR_ITERATIONS,
        "token_budget_limit": settings.FINOPS_MAX_TOKENS_PER_INCIDENT,
        "total_tokens_consumed": 250,
        "is_budget_exceeded": False,
        "trace_id": f"trace-{incident_id}",
        "langsmith_run_id": None,
    }

    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Run workflow until it halts at the HITL gate
        await graph_app.ainvoke(initial_state, config=config)
        snapshot = await graph_app.aget_state(config)
        state_values = snapshot.values
        now_iso = datetime.now(UTC).isoformat()

        # Save to registry
        registry[incident_id] = {
            "thread_id": thread_id,
            "values": {
                **state_values,
                "created_at": now_iso,
                "service": payload.service,
            },
        }

        return IncidentResponse(
            incident_id=incident_id,
            severity=state_values.get("severity", payload.severity),
            status=state_values.get("status", "AWAITING_APPROVAL"),
            service=payload.service,
            created_at=now_iso,
            root_cause_summary=state_values.get("root_cause_summary"),
            remediation_plan=state_values.get("remediation_plan"),
            retrieved_sources=state_values.get("retrieved_sources", []),
            total_tokens_consumed=state_values.get("total_tokens_consumed", 250),
            is_budget_exceeded=state_values.get("is_budget_exceeded", False),
            agent_results=state_values.get("agent_results", {}),
            human_approved=state_values.get("human_approved"),
            approved_by=state_values.get("approved_by"),
            approval_timestamp=state_values.get("approval_timestamp"),
        )
    except Exception as exc:
        logger.error("Error executing LangGraph for incident %s: %s", incident_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha na orquestração do incidente: {exc}",
        ) from exc


@router.get(
    "",
    response_model=list[IncidentResponse],
    summary="Listar Histórico Completo de Incidentes & Auditoria",
)
async def list_incidents(
    severity: str | None = Query(
        default=None, description="Filtrar por severidade (ex: P0_CRITICAL, P1_HIGH)"
    ),
    status: str | None = Query(
        default=None, description="Filtrar por status (ex: RESOLVED, AWAITING_APPROVAL)"
    ),
    limit: int = Query(default=50, ge=1, le=100, description="Limite de incidentes a retornar"),
    registry: dict = Depends(get_incident_registry),
) -> list[IncidentResponse]:
    """Retrieve the historical ledger of all incidents recorded in the system, sorted newest first."""
    items: list[IncidentResponse] = []
    for inc_id, entry in reversed(list(registry.items())):
        values = entry.get("values", {})
        item_severity = values.get("severity", "P1_HIGH")
        item_status = values.get("status", "INVESTIGATING")

        if severity and item_severity != severity:
            continue
        if status and item_status != status:
            continue

        items.append(
            IncidentResponse(
                incident_id=inc_id,
                severity=item_severity,
                status=item_status,
                service=values.get("service")
                or values.get("raw_alert_sanitized", {}).get("service", "core-service"),
                created_at=values.get("created_at"),
                root_cause_summary=values.get("root_cause_summary"),
                remediation_plan=values.get("remediation_plan"),
                retrieved_sources=values.get("retrieved_sources", []),
                total_tokens_consumed=values.get("total_tokens_consumed", 0),
                is_budget_exceeded=values.get("is_budget_exceeded", False),
                agent_results=values.get("agent_results", {}),
                human_approved=values.get("human_approved"),
                approved_by=values.get("approved_by"),
                approval_timestamp=values.get("approval_timestamp"),
            )
        )
        if len(items) >= limit:
            break

    return items


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Consultar Estado Atual e Evidências do Incidente",
)
async def get_incident_status(
    incident_id: str,
    graph_app: Any = Depends(get_graph_app),
    registry: dict = Depends(get_incident_registry),
) -> IncidentResponse:
    """Retrieve the live LangGraph state checkpoint for a given incident."""
    reg = registry.get(incident_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente '{incident_id}' não encontrado.",
        )

    thread_id = reg["thread_id"]
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await graph_app.aget_state(config)
    values = snapshot.values if snapshot else reg["values"]

    return IncidentResponse(
        incident_id=incident_id,
        severity=values.get("severity", "P1_HIGH"),
        status=values.get("status", "INVESTIGATING"),
        service=values.get("service")
        or values.get("raw_alert_sanitized", {}).get("service", "core-service"),
        created_at=values.get("created_at"),
        root_cause_summary=values.get("root_cause_summary"),
        remediation_plan=values.get("remediation_plan"),
        retrieved_sources=values.get("retrieved_sources", []),
        total_tokens_consumed=values.get("total_tokens_consumed", 0),
        is_budget_exceeded=values.get("is_budget_exceeded", False),
        agent_results=values.get("agent_results", {}),
        human_approved=values.get("human_approved"),
        approved_by=values.get("approved_by"),
        approval_timestamp=values.get("approval_timestamp"),
    )


@router.post(
    "/{incident_id}/resume",
    response_model=IncidentResponse,
    summary="Portão HITL: Autorizar ou Rejeitar Mitigação Cirúrgica",
)
async def resume_incident(
    incident_id: str,
    payload: ResumeIncidentRequest,
    graph_app: Any = Depends(get_graph_app),
    registry: dict = Depends(get_incident_registry),
) -> IncidentResponse:
    """Resume execution of an incident paused at the HITL gate with human signoff."""
    reg = registry.get(incident_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente '{incident_id}' não encontrado.",
        )

    thread_id = reg["thread_id"]
    config = {"configurable": {"thread_id": thread_id}}

    now_iso = datetime.now(UTC).isoformat()
    old_values = reg.get("values", {})
    is_replay = incident_id.startswith("INC-REPLAY") or reg.get("is_replay", False)

    if is_replay:
        # Replay sandbox: deterministic fast path without invoking graph_app on uninitialized thread
        new_status = "RESOLVED" if payload.human_approved else "FAILED"
        final_values = {
            **old_values,
            "status": new_status,
            "human_approved": payload.human_approved,
            "approved_by": payload.approved_by,
            "approval_timestamp": now_iso,
        }
        reg["values"] = final_values
    else:
        thread_id = reg["thread_id"]
        config = {"configurable": {"thread_id": thread_id}}

        await graph_app.aupdate_state(
            config,
            {
                "human_approved": payload.human_approved,
                "approved_by": payload.approved_by,
                "approval_timestamp": now_iso,
            },
            as_node="remediation_node",
        )

        # Resume graph execution
        await graph_app.ainvoke(None, config=config)
        snapshot = await graph_app.aget_state(config)
        graph_values = snapshot.values if snapshot else {}

        # Merge carefully so specialist evidence from initial investigation is never lost
        merged_agent_results = {
            **old_values.get("agent_results", {}),
            **graph_values.get("agent_results", {}),
        }
        final_values = {
            **old_values,
            **graph_values,
            "agent_results": merged_agent_results,
        }
        reg["values"] = final_values

    return IncidentResponse(
        incident_id=incident_id,
        severity=final_values.get("severity", "P1_HIGH"),
        status=final_values.get("status", "RESOLVED"),
        service=final_values.get("service")
        or final_values.get("raw_alert_sanitized", {}).get("service", "core-service"),
        created_at=final_values.get("created_at"),
        root_cause_summary=final_values.get("root_cause_summary"),
        remediation_plan=final_values.get("remediation_plan"),
        retrieved_sources=final_values.get("retrieved_sources", []),
        total_tokens_consumed=final_values.get("total_tokens_consumed", 0),
        is_budget_exceeded=final_values.get("is_budget_exceeded", False),
        agent_results=final_values.get("agent_results", {}),
        human_approved=final_values.get("human_approved"),
        approved_by=final_values.get("approved_by"),
        approval_timestamp=final_values.get("approval_timestamp"),
    )


@router.get(
    "/{incident_id}/post-mortem",
    summary="Gerar Relatório Post-Mortem de Auditoria (JSON ou PDF)",
)
async def get_post_mortem(
    incident_id: str,
    format: Literal["json", "pdf"] = Query(
        default="json", description="Formato do post-mortem ('json' ou 'pdf')"
    ),
    registry: dict = Depends(get_incident_registry),
) -> Any:
    """Retrieve the cryptographically verified PostMortemReport or download as PDF."""
    reg = registry.get(incident_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente '{incident_id}' não encontrado.",
        )

    values = reg["values"]
    pm_data = values.get("agent_results", {}).get("PostMortemReport")

    agent = AuditPostMortemAgent()
    if not pm_data:
        # Generate on the fly if not resolved yet
        report = agent.generate_report(
            incident_id=incident_id,
            severity=values.get("severity", "P1_HIGH"),
            root_cause_summary=values.get("root_cause_summary"),
            remediation_plan=values.get("remediation_plan"),
            raw_alert=values.get("raw_alert_sanitized", {}),
            approved_by=values.get("approved_by"),
            approval_timestamp=values.get("approval_timestamp"),
        )
    else:
        report = PostMortemReport(**pm_data)

    if format == "pdf":
        pdf_bytes = agent.export_pdf(report)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=post-mortem-{incident_id}.pdf"},
        )

    return report
