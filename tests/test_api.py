import pytest
from httpx import ASGITransport, AsyncClient

from opsmesh.api.app import app


@pytest.mark.asyncio
async def test_health_and_scalar_docs_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res_health = await client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"

        # 2. Scalar docs at /docs
        res_docs = await client.get("/docs")
        assert res_docs.status_code == 200
        assert "scalar" in res_docs.text.lower()

        # 3. Scalar docs alias at /scalar
        res_scalar = await client.get("/scalar")
        assert res_scalar.status_code == 200
        assert "scalar" in res_scalar.text.lower()

        # 4. Frontend SPA serving at / (200 if frontend dist exists, or 404 in headless CI)
        res_spa = await client.get("/")
        assert res_spa.status_code in (200, 404)
        if res_spa.status_code == 200:
            assert "OpsMesh" in res_spa.text


@pytest.mark.asyncio
async def test_incident_lifecycle_via_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Webhook alert ingestion
        alert_payload = {
            "service": "order-service",
            "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections on node 10.244.1.15",
            "severity": "P0_CRITICAL",
            "metadata": {"client_ip": "203.0.113.195"},
        }
        res_ingest = await client.post("/api/v1/incidents/webhook", json=alert_payload)
        assert res_ingest.status_code == 202
        data = res_ingest.json()
        incident_id = data["incident_id"]
        assert incident_id.startswith("INC-")
        assert data["status"] == "AWAITING_APPROVAL"
        assert data["remediation_plan"] is not None

        # 2. Query status
        res_status = await client.get(f"/api/v1/incidents/{incident_id}")
        assert res_status.status_code == 200
        assert res_status.json()["incident_id"] == incident_id

        # 3. Resume with HITL approval
        resume_payload = {
            "human_approved": True,
            "approved_by": "oncall-sre@company.com",
            "operator_notes": "Aprovada terminação de conexões ociosas",
        }
        res_resume = await client.post(
            f"/api/v1/incidents/{incident_id}/resume", json=resume_payload
        )
        assert res_resume.status_code == 200
        assert res_resume.json()["status"] == "RESOLVED"

        # 4. Get Post-Mortem JSON
        res_pm_json = await client.get(f"/api/v1/incidents/{incident_id}/post-mortem?format=json")
        assert res_pm_json.status_code == 200
        pm_data = res_pm_json.json()
        assert pm_data["incident_id"] == incident_id
        assert len(pm_data["cryptographic_audit_hash"]) == 64

        # 5. Get Post-Mortem PDF
        res_pm_pdf = await client.get(f"/api/v1/incidents/{incident_id}/post-mortem?format=pdf")
        assert res_pm_pdf.status_code == 200
        assert res_pm_pdf.headers["content-type"] == "application/pdf"
        assert res_pm_pdf.content.startswith(b"%PDF")

        # 6. List Incidents History
        res_history = await client.get("/api/v1/incidents")
        assert res_history.status_code == 200
        history_list = res_history.json()
        assert len(history_list) >= 1
        history_ids = [item["incident_id"] for item in history_list]
        assert incident_id in history_ids
        # Check audit fields
        first_item = history_list[0]
        assert "incident_id" in first_item
        assert "status" in first_item
        assert "severity" in first_item
