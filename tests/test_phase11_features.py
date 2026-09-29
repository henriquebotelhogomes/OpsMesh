"""Unit and Integration Tests for Phase 11 Features.

Covers:
- GitHub REST API source inspection tool
- Two-Tier Remediation (Runtime Mitigation & GitOps PR)
- OpenRouter Gateway & Jev Decision Engine
- Distributed Tracing Context (W3C traceparent & Datadog)
- DuckDB + Parquet Serverless Columnar Analytics
- BYOK Headers and Analytics API endpoint
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from opsmesh.agents.log_analyst import LogTraceAnalystAgent
from opsmesh.agents.remediation import RemediationEngineerAgent
from opsmesh.agents.supervisor import IncidentSupervisorAgent
from opsmesh.api.app import app
from opsmesh.core.state import IncidentState
from opsmesh.core.tracing import extract_trace_context, trace_async_span, trace_span
from opsmesh.gateway.openrouter import JevDecisionEngine, OpenRouterClient
from opsmesh.gateway.tools import inspect_github_source
from opsmesh.storage.analytics import query_incident_metrics, record_incident_analytics


def test_inspect_github_source_tool() -> None:
    """Verify GitHub source inspection tool returns formatted snippet with line numbers."""
    snippet = inspect_github_source(
        repo="henriquebotelhogomes/chaos-lab",
        file_path="shopcore-api/app/routers/checkout.py",
        start_line=1,
        end_line=15,
        ref="main",
    )
    assert "// File: henriquebotelhogomes/chaos-lab" in snippet
    assert "1:" in snippet
    assert len(snippet) <= 2000


@pytest.mark.asyncio
async def test_log_analyst_agent_github_source_inspection() -> None:
    """Verify LogTraceAnalystAgent populates source_file_reference and code snippet."""
    analyst = LogTraceAnalystAgent()
    res = await analyst.analyze("checkout timeout 504")

    assert res.source_file_reference is not None
    assert "checkout.py" in res.source_file_reference
    assert res.inspected_code_snippet is not None
    assert "1:" in res.inspected_code_snippet


@pytest.mark.asyncio
async def test_two_tier_remediation_plan() -> None:
    """Verify RemediationEngineerAgent builds both Tier 1 and Tier 2 plans."""
    agent = RemediationEngineerAgent()
    plan = await agent.plan(
        root_cause_summary="PostgreSQL connection pool exhausted",
        agent_results={},
        raw_alert={"service": "order-service", "description": "TooManyConnectionsError"},
    )

    # Base backward-compatible fields
    assert plan.action_type == "DATABASE_TERMINATE_BACKENDS"
    assert len(plan.proposed_commands) > 0
    assert plan.patch_diff is not None

    # Tier 1: Runtime Mitigation
    assert plan.tier_1_runtime is not None
    assert plan.tier_1_runtime.action_type == "DATABASE_TERMINATE_BACKENDS"
    assert plan.tier_1_runtime.target_endpoint == "POST /operations/mitigate"

    # Tier 2: GitOps Pull Request
    assert plan.tier_2_gitops is not None
    assert plan.tier_2_gitops.target_repo == "henriquebotelhogomes/chaos-lab"
    assert "fix/" in plan.tier_2_gitops.pr_branch_name
    assert "fix(db)" in plan.tier_2_gitops.pr_title
    assert plan.tier_2_gitops.patch_diff is not None


@pytest.mark.asyncio
async def test_openrouter_gateway_and_jev_engine() -> None:
    """Verify OpenRouter client and Jev Decision Engine routing logic."""
    client = OpenRouterClient(api_key="test-mock-key")
    assert client.is_configured is True

    engine = JevDecisionEngine(client=client)

    # Initial turn: dispatch specialists
    decision_initial = await engine.evaluate_convergence_and_routing(
        severity="P1_HIGH",
        iteration_count=1,
        max_iterations=4,
        alert_description="Latency spike in checkout service",
        agent_results={},
    )
    assert decision_initial.is_investigation_complete is False
    assert len(decision_initial.next_steps) == 3

    # Converged turn: with specialist results
    decision_converged = await engine.evaluate_convergence_and_routing(
        severity="P1_HIGH",
        iteration_count=2,
        max_iterations=4,
        alert_description="Latency spike",
        agent_results={
            "LogTraceAnalystAgent": {"summary": "Timeout in payment gateway"},
            "DatabaseInfraAgent": {"diagnostic_evidence": "Pool utilization at 95%"},
        },
    )
    assert decision_converged.is_investigation_complete is True
    assert decision_converged.root_cause_hypothesis is not None
    assert "Timeout" in decision_converged.root_cause_hypothesis


@pytest.mark.asyncio
async def test_supervisor_agent_with_jev() -> None:
    """Verify IncidentSupervisorAgent initializes and runs with Jev Decision Engine."""
    supervisor = IncidentSupervisorAgent(provider="openrouter")
    assert supervisor.jev_engine is not None

    state: IncidentState = {
        "incident_id": "INC-TEST-JEV-01",
        "severity": "P0_CRITICAL",
        "status": "INVESTIGATING",
        "raw_alert_sanitized": {"description": "Postgres pool crash"},
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
        "total_tokens_consumed": 200,
        "is_budget_exceeded": False,
        "trace_id": "trace-test",
        "langsmith_run_id": None,
    }

    decision = await supervisor.decide(state)
    assert decision.is_investigation_complete is False
    assert len(decision.next_steps) == 3


def test_distributed_tracing_extraction() -> None:
    """Verify extraction of W3C traceparent and Datadog trace context."""
    headers = {
        "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        "x-datadog-trace-id": "1234567890",
    }
    ctx = extract_trace_context(headers=headers)
    assert ctx["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert ctx["span_id"] == "00f067aa0ba902b7"
    assert ctx["datadog_trace_id"] == "1234567890"

    # Context manager test
    with trace_span("test_span", resource="test_resource") as span:
        assert span["span_name"] == "test_span"
        assert "span_id" in span


@pytest.mark.asyncio
async def test_trace_async_span() -> None:
    """Verify async tracing span context manager."""
    async with trace_async_span("async_agent_node") as span:
        assert span["span_name"] == "async_agent_node"


def test_duckdb_parquet_analytics() -> None:
    """Verify recording and querying analytics using DuckDB and Parquet."""
    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_file = str(Path(tmpdir) / "test_incidents.parquet")

        record_incident_analytics(
            {
                "incident_id": "INC-TEST-ANALYTICS-01",
                "service": "shopcore-api",
                "severity": "P0_CRITICAL",
                "status": "RESOLVED",
                "total_duration_minutes": 3.2,
                "estimated_cost_avoided_usd": 25000.0,
                "root_cause_summary": "Database pool locked by deadlocks",
            },
            parquet_path=parquet_file,
        )

        metrics = query_incident_metrics(parquet_path=parquet_file)
        assert metrics["total_incidents"] == 1
        assert metrics["avg_mttr_minutes"] == 3.2
        assert metrics["total_cost_avoided_usd"] == 25000.0
        assert metrics["service_breakdown"].get("shopcore-api") == 1


@pytest.mark.asyncio
async def test_analytics_api_endpoint() -> None:
    """Verify GET /api/v1/incidents/analytics/metrics returns valid JSON summary."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/incidents/analytics/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_incidents" in data
        assert "avg_mttr_minutes" in data
        assert "total_cost_avoided_usd" in data
