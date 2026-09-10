"""Tests for PII sanitization and FinOps Circuit Breaker."""

from opsmesh.core.circuit_breaker import DailyTokenCircuitBreaker
from opsmesh.core.pii_sanitizer import sanitize_payload, sanitize_text
from opsmesh.core.schemas import SupervisorDecision
from opsmesh.core.state import reduce_agent_results, reduce_sources


def test_pii_sanitizer_preserves_rfc_1918_and_redacts_wan():
    log_line = (
        "User 123.45.67.89 accessed pod at 10.244.1.15 and database at 172.16.0.5. "
        "CPF: 123.456.789-00, email: dev@corp.com, password=super_secret_123"
    )
    sanitized = sanitize_text(log_line)

    # Verifica que IP público foi mascarado
    assert "123.45.67.89" not in sanitized
    assert "[REDACTED_PUBLIC_IP]" in sanitized

    # Verifica que IPs privados RFC 1918 foram PRESERVADOS
    assert "10.244.1.15" in sanitized
    assert "172.16.0.5" in sanitized

    # Verifica que dados pessoais e senhas foram mascarados
    assert "123.456.789-00" not in sanitized
    assert "[REDACTED_CPF]" in sanitized
    assert "dev@corp.com" not in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "super_secret_123" not in sanitized
    assert "[REDACTED_CREDENTIAL]" in sanitized


def test_sanitize_payload_recursive():
    payload = {
        "alert": "Spike on WAN IP 200.100.50.25",
        "nested": {
            "internal_ip": "192.168.1.100",
            "token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-IDcSemACt8x4iTMCda8Yhe3iZaWbvV5XKSTbuAn0M",
        },
    }
    sanitized = sanitize_payload(payload)
    assert "[REDACTED_PUBLIC_IP]" in sanitized["alert"]
    assert "192.168.1.100" in sanitized["nested"]["internal_ip"]
    assert "[REDACTED_TOKEN]" in sanitized["nested"]["token"]


def test_circuit_breaker_enforces_budget_and_allows_byok():
    cb = DailyTokenCircuitBreaker(token_limit=1000)

    # Initial state
    allowed, _ = cb.check_allowed(is_byok=False)
    assert allowed is True

    # Consome 800 tokens
    cb.record_consumption(800)
    allowed, _ = cb.check_allowed(is_byok=False)
    assert allowed is True

    # Consome mais 300 tokens (total 1100 > 1000)
    cb.record_consumption(300)
    allowed, msg = cb.check_allowed(is_byok=False)
    assert allowed is False
    assert "Cota diária de demonstração pública atingida" in msg

    # BYOK bypass deve permitir mesmo com o disjuntor desarmado!
    byok_allowed, _ = cb.check_allowed(is_byok=True)
    assert byok_allowed is True


def test_state_reducers():
    # Test reduce_agent_results
    curr = {"agent_a": {"status": "ok"}}
    update = {"agent_b": {"status": "done"}}
    merged = reduce_agent_results(curr, update)
    assert "agent_a" in merged
    assert "agent_b" in merged

    # Reset with {}
    reset = reduce_agent_results(merged, {})
    assert reset == {}

    # Test reduce_sources
    sources = ["runbook_1.md"]
    new_sources = ["runbook_1.md", "runbook_2.md"]
    merged_s = reduce_sources(sources, new_sources)
    assert merged_s == ["runbook_1.md", "runbook_2.md"]

    # Reset with []
    assert reduce_sources(merged_s, []) == []


def test_supervisor_decision_schema():
    decision = SupervisorDecision(
        incident_severity="P0_CRITICAL",
        is_investigation_complete=False,
        next_steps=[
            {
                "agent_name": "LogTraceAnalystAgent",
                "reasoning": "Investigar pico de 500 no checkout",
                "input_directive": "Buscar logs de checkout nos últimos 15 min",
            }
        ],
        root_cause_hypothesis="Possível falha de schema no checkout",
    )
    assert decision.incident_severity == "P0_CRITICAL"
    assert len(decision.next_steps) == 1
