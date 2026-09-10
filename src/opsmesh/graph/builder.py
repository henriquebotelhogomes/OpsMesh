"""LangGraph Incident Commander Graph Builder.

Assembles the multi-agent StateGraph with parallel specialist diagnostics,
conditional routing, Human-in-the-Loop (HITL) execution gate, and serverless checkpoints.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from langgraph.graph import END, START, StateGraph

from opsmesh.agents.infra_analyst import DatabaseInfraAgent
from opsmesh.agents.log_analyst import LogTraceAnalystAgent
from opsmesh.agents.post_mortem import AuditPostMortemAgent
from opsmesh.agents.remediation import RemediationEngineerAgent
from opsmesh.agents.runbook_agent import RunbookKnowledgeAgent
from opsmesh.agents.supervisor import IncidentSupervisorAgent
from opsmesh.core.state import IncidentState
from opsmesh.graph.checkpointer import get_checkpointer

logger = logging.getLogger(__name__)


async def build_incident_graph(checkpointer: Any = None) -> Any:
    """Build and compile the OpsMesh Incident Commander LangGraph."""
    if checkpointer is None:
        checkpointer = await get_checkpointer()

    supervisor = IncidentSupervisorAgent()
    log_analyst = LogTraceAnalystAgent()
    infra_analyst = DatabaseInfraAgent()
    runbook_agent = RunbookKnowledgeAgent()
    remediation_agent = RemediationEngineerAgent()
    post_mortem_agent = AuditPostMortemAgent()

    # --- Node Definitions ---

    async def supervisor_node(state: IncidentState) -> dict[str, Any]:
        """Evaluate current crisis evidence and decide next step."""
        decision = await supervisor.decide(state)

        if decision.is_investigation_complete:
            return {
                "root_cause_summary": decision.root_cause_hypothesis,
                "status": "INVESTIGATING",
            }

        curr_count = state.get("iteration_count", 1)
        return {
            "iteration_count": curr_count + 1,
            "status": "INVESTIGATING",
        }

    def supervisor_router(state: IncidentState) -> str:
        """Route conditionally based on investigation completion."""
        if state.get("root_cause_summary") is not None:
            return "remediation_node"
        if state.get("iteration_count", 1) >= state.get("max_iterations", 4):
            return "remediation_node"
        return "diagnostics_node"

    async def diagnostics_node(state: IncidentState) -> dict[str, Any]:
        """Execute specialist agents in parallel to gather evidence."""
        raw_alert = state.get("raw_alert_sanitized", {})
        alert_desc = str(raw_alert.get("description") or raw_alert.get("message") or raw_alert)

        log_task = log_analyst.analyze(alert_desc)
        infra_task = infra_analyst.analyze(alert_desc)
        runbook_task = runbook_agent.retrieve(alert_desc)

        log_res, infra_res, runbook_res = await asyncio.gather(log_task, infra_task, runbook_task)

        sources = [rec.source_file for rec in runbook_res.recommendations]

        return {
            "agent_results": {
                "LogTraceAnalystAgent": log_res.model_dump(),
                "DatabaseInfraAgent": infra_res.model_dump(),
                "RunbookKnowledgeAgent": runbook_res.model_dump(),
            },
            "retrieved_sources": sources,
        }

    async def remediation_node(state: IncidentState) -> dict[str, Any]:
        """Formulate remediation plan and pause at HITL gate."""
        raw_alert = state.get("raw_alert_sanitized", {})
        root_cause = state.get("root_cause_summary") or "Degradação sistêmica detectada"
        agent_results = state.get("agent_results", {})

        plan = await remediation_agent.plan(root_cause, agent_results, raw_alert)

        return {
            "remediation_plan": plan.model_dump(),
            "status": "AWAITING_APPROVAL",
        }

    async def execute_remediation_node(state: IncidentState) -> dict[str, Any]:
        """Execute approved mitigation commands or reject."""
        approved = state.get("human_approved", False)

        if not approved:
            return {
                "status": "FAILED",
                "error_message": "Mitigação rejeitada ou abortada pelo operador SRE.",
            }

        return {
            "status": "MITIGATING",
        }

    async def post_mortem_node(state: IncidentState) -> dict[str, Any]:
        """Generate final audit report and conclude incident."""
        report = post_mortem_agent.generate_report(
            incident_id=state.get("incident_id", "INC-UNKNOWN"),
            severity=state.get("severity", "P1_HIGH"),
            root_cause_summary=state.get("root_cause_summary"),
            remediation_plan=state.get("remediation_plan"),
            raw_alert=state.get("raw_alert_sanitized", {}),
            approved_by=state.get("approved_by"),
            approval_timestamp=state.get("approval_timestamp"),
        )

        return {
            "status": "RESOLVED",
            "agent_results": {
                "PostMortemReport": report.model_dump(),
            },
        }

    # --- Assemble Workflow Graph ---

    workflow = StateGraph(IncidentState)

    workflow.add_node("supervisor_node", supervisor_node)
    workflow.add_node("diagnostics_node", diagnostics_node)
    workflow.add_node("remediation_node", remediation_node)
    workflow.add_node("execute_remediation_node", execute_remediation_node)
    workflow.add_node("post_mortem_node", post_mortem_node)

    # Edges
    workflow.add_edge(START, "supervisor_node")
    workflow.add_conditional_edges(
        "supervisor_node",
        supervisor_router,
        {
            "diagnostics_node": "diagnostics_node",
            "remediation_node": "remediation_node",
        },
    )
    workflow.add_edge("diagnostics_node", "supervisor_node")
    workflow.add_edge("remediation_node", "execute_remediation_node")
    workflow.add_edge("execute_remediation_node", "post_mortem_node")
    workflow.add_edge("post_mortem_node", END)

    # Compile with HITL interrupt before execution of remediation commands
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute_remediation_node"],
    )
    return app
