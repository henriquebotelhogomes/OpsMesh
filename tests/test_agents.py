import pytest

from opsmesh.agents.infra_analyst import DatabaseInfraAgent
from opsmesh.agents.log_analyst import LogTraceAnalystAgent
from opsmesh.agents.post_mortem import AuditPostMortemAgent
from opsmesh.agents.remediation import RemediationEngineerAgent
from opsmesh.agents.runbook_agent import RunbookKnowledgeAgent
from opsmesh.agents.supervisor import IncidentSupervisorAgent
from opsmesh.core.state import IncidentState


@pytest.mark.asyncio
async def test_supervisor_initial_and_completion_decision():
    supervisor = IncidentSupervisorAgent()
    state: IncidentState = {
        "incident_id": "inc-test-01",
        "severity": "P0_CRITICAL",
        "status": "INVESTIGATING",
        "raw_alert_sanitized": {"message": "PostgreSQL connection pool exhausted"},
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
        "total_tokens_consumed": 500,
        "is_budget_exceeded": False,
        "trace_id": "trace-123",
        "langsmith_run_id": None,
    }

    # Turn 1: Should delegate to specialists
    dec1 = await supervisor.decide(state)
    assert not dec1.is_investigation_complete
    assert len(dec1.next_steps) >= 3

    # Turn 2: With results present, should complete
    state["agent_results"] = {
        "LogTraceAnalystAgent": {"summary": "TooManyConnectionsError detected"},
        "DatabaseInfraAgent": {"diagnostic_evidence": "Pool at 98%"},
    }
    dec2 = await supervisor.decide(state)
    assert dec2.is_investigation_complete
    assert dec2.root_cause_hypothesis is not None


@pytest.mark.asyncio
async def test_supervisor_max_turn_guardrail():
    supervisor = IncidentSupervisorAgent()
    state: IncidentState = {
        "incident_id": "inc-test-02",
        "severity": "P1_HIGH",
        "status": "INVESTIGATING",
        "raw_alert_sanitized": {"message": "Unknown latency issue"},
        "messages": [],
        "agent_results": {},
        "retrieved_sources": [],
        "root_cause_summary": None,
        "remediation_plan": None,
        "error_message": None,
        "human_approved": None,
        "approved_by": None,
        "approval_timestamp": None,
        "iteration_count": 4,  # Reached limit
        "max_iterations": 4,
        "token_budget_limit": 12000,
        "total_tokens_consumed": 11500,
        "is_budget_exceeded": False,
        "trace_id": "trace-124",
        "langsmith_run_id": None,
    }
    dec = await supervisor.decide(state)
    assert dec.is_investigation_complete


@pytest.mark.asyncio
async def test_log_analyst_agent():
    agent = LogTraceAnalystAgent()
    res = await agent.analyze("Buscar erros de postgres")
    assert res.error_spike_percentage > 0
    assert (
        "order-service" in res.probable_origin_service or "unknown" in res.probable_origin_service
    )


@pytest.mark.asyncio
async def test_infra_analyst_agent():
    agent = DatabaseInfraAgent()
    res = await agent.analyze("pool de conexoes postgres")
    assert res.database_pool_utilization_pct >= 90.0
    assert res.is_resource_exhausted


@pytest.mark.asyncio
async def test_runbook_agent():
    agent = RunbookKnowledgeAgent()
    res = await agent.retrieve("pool conexões postgres")
    assert len(res.recommendations) > 0
    assert "SOP-DB-002" in res.recommendations[0].runbook_title


@pytest.mark.asyncio
async def test_remediation_agent():
    agent = RemediationEngineerAgent()
    plan = await agent.plan(
        root_cause_summary="PostgreSQL pool exhausted with 98% saturation",
        agent_results={},
        raw_alert={"message": "db error"},
    )
    assert plan.action_type == "DATABASE_TERMINATE_BACKENDS"
    assert plan.is_critical_action is True
    assert len(plan.proposed_commands) > 0
    assert plan.patch_diff is not None


def test_post_mortem_report_and_pdf():
    agent = AuditPostMortemAgent()
    report = agent.generate_report(
        incident_id="INC-2026-001",
        severity="P0_CRITICAL",
        root_cause_summary="Vazamento de conexões no order-service",
        remediation_plan={
            "proposed_commands": ["SELECT pg_terminate_backend(10492)"],
            "rollback_plan": "restart",
        },
        raw_alert={"service": "order-service"},
        approved_by="sre-lead@enterprise.com",
    )
    assert report.incident_id == "INC-2026-001"
    assert len(report.cryptographic_audit_hash) == 64
    assert len(report.timeline) >= 5

    pdf_bytes = agent.export_pdf(report)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
