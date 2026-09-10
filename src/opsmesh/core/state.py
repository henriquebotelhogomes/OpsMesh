"""OpsMesh Shared IncidentState and Reducers."""

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


def reduce_agent_results(current: dict | None, update: dict | None) -> dict:
    """Reducer com suporte a merge de resultados de agentes e reset via update={}."""
    if update is None:
        return current or {}
    if update == {}:
        return {}
    return {**(current or {}), **update}


def reduce_sources(current: list | None, update: list | None) -> list:
    """Reducer para fontes consultadas com desduplicação e reset via update=[]."""
    if update is None:
        return current or []
    if update == []:
        return []
    curr = current or []
    return curr + [s for s in update if s not in curr]


class IncidentState(TypedDict):
    # Metadados e Ciclo de Vida
    incident_id: str
    severity: Literal["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
    status: Literal["INVESTIGATING", "AWAITING_APPROVAL", "MITIGATING", "RESOLVED", "FAILED"]
    raw_alert_sanitized: dict

    # Mensagens e Evidências Reduzidas
    messages: Annotated[list[AnyMessage], add_messages]
    agent_results: Annotated[dict, reduce_agent_results]
    retrieved_sources: Annotated[list, reduce_sources]

    # Diagnóstico e Plano Tipados
    root_cause_summary: str | None
    remediation_plan: dict | None
    error_message: str | None

    # Portão Human-in-the-Loop (HITL)
    human_approved: bool | None
    approved_by: str | None
    approval_timestamp: str | None

    # Guardrails FinOps & Limites de Execução
    iteration_count: int
    max_iterations: int
    token_budget_limit: int
    total_tokens_consumed: int
    is_budget_exceeded: bool

    # Observabilidade e Rastreabilidade (LangSmith / Langfuse)
    trace_id: str | None
    langsmith_run_id: str | None
