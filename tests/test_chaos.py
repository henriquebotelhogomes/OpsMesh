import pytest
from httpx import ASGITransport, AsyncClient

from opsmesh.api.app import app
from opsmesh.chaos.studio import SCENARIOS, ChaosStudio


def test_chaos_studio_scenarios_listing():
    scenarios = ChaosStudio.list_scenarios()
    assert len(scenarios) == 4
    scenario_ids = [s["id"] for s in scenarios]
    assert "postgres-pool" in scenario_ids
    assert "checkout-timeout" in scenario_ids
    assert "payment-latency" in scenario_ids
    assert "model-drift-oom" in scenario_ids


@pytest.mark.asyncio
async def test_zero_token_replay_mode():
    for scenario_id in SCENARIOS:
        response = await ChaosStudio.simulate_scenario(scenario_id, demo_mode="replay")
        assert response.total_tokens_consumed == 0
        assert response.status == "AWAITING_APPROVAL"
        assert response.remediation_plan is not None
        assert len(response.remediation_plan["proposed_commands"]) > 0


@pytest.mark.asyncio
async def test_chaos_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. List scenarios
        res_list = await client.get("/api/v1/chaos/scenarios")
        assert res_list.status_code == 200
        scenarios = res_list.json()
        assert len(scenarios) == 4

        # 2. Trigger Replay simulation
        res_sim = await client.post("/api/v1/chaos/simulate/postgres-pool?mode=replay")
        assert res_sim.status_code == 200
        data = res_sim.json()
        assert data["total_tokens_consumed"] == 0
        assert data["severity"] == "P0_CRITICAL"
        assert "DATABASE_TERMINATE_BACKENDS" in data["remediation_plan"]["action_type"]

        # 3. Trigger nonexistent scenario
        res_err = await client.post("/api/v1/chaos/simulate/nonexistent-scenario")
        assert res_err.status_code == 404

        # 4. Resume the simulated incident and verify agent_results preservation
        res_resume = await client.post(
            f"/api/v1/incidents/{data['incident_id']}/resume",
            json={
                "human_approved": True,
                "approved_by": "sre-test@enterprise.org",
                "notes": "Mitigação autorizada",
            },
        )
        assert res_resume.status_code == 200
        resumed_data = res_resume.json()
        assert resumed_data["status"] == "RESOLVED"
        assert "LogTraceAnalystAgent" in resumed_data["agent_results"]
        assert "summary" in resumed_data["agent_results"]["LogTraceAnalystAgent"]
        assert "DatabaseInfraAgent" in resumed_data["agent_results"]
        assert "RunbookKnowledgeAgent" in resumed_data["agent_results"]
