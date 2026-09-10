import pytest
from langgraph.checkpoint.memory import MemorySaver

from opsmesh.core.state import IncidentState
from opsmesh.graph.builder import build_incident_graph


@pytest.mark.asyncio
async def test_langgraph_incident_workflow_and_hitl_gate():
    # 1. Initialize checkpointer and graph
    checkpointer = MemorySaver()
    app = await build_incident_graph(checkpointer=checkpointer)

    initial_state: IncidentState = {
        "incident_id": "INC-TEST-999",
        "severity": "P0_CRITICAL",
        "status": "INVESTIGATING",
        "raw_alert_sanitized": {
            "service": "order-service",
            "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections",
            "source": "datadog",
        },
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
        "trace_id": "trace-test-999",
        "langsmith_run_id": None,
    }

    config = {"configurable": {"thread_id": "thread-test-999"}}

    # 2. First phase: run until HITL interrupt
    _ = await app.ainvoke(initial_state, config=config)

    # Assert that execution halted before execute_remediation_node
    snapshot = await app.aget_state(config)
    assert snapshot.next == ("execute_remediation_node",)

    # Verify state at pause
    assert snapshot.values["status"] == "AWAITING_APPROVAL"
    assert snapshot.values["remediation_plan"] is not None
    assert len(snapshot.values["remediation_plan"]["proposed_commands"]) > 0
    assert "LogTraceAnalystAgent" in snapshot.values["agent_results"]
    assert "DatabaseInfraAgent" in snapshot.values["agent_results"]

    # 3. Resume with Human Approval (HITL Destravamento)
    await app.aupdate_state(
        config,
        {
            "human_approved": True,
            "approved_by": "sre-engineer@enterprise.org",
            "approval_timestamp": "2026-09-10T00:50:00Z",
        },
        as_node="remediation_node",
    )

    # Resume execution by passing None to ainvoke
    _ = await app.ainvoke(None, config=config)

    # Assert final resolved state
    final_snapshot = await app.aget_state(config)
    assert final_snapshot.next == ()  # Reached END
    assert final_snapshot.values["status"] == "RESOLVED"
    assert "PostMortemReport" in final_snapshot.values["agent_results"]

    post_mortem = final_snapshot.values["agent_results"]["PostMortemReport"]
    assert post_mortem["incident_id"] == "INC-TEST-999"
    assert len(post_mortem["cryptographic_audit_hash"]) == 64
