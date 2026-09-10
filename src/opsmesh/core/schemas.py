"""OpsMesh Pydantic v2 Schemas and Contracts."""

from typing import Literal

from pydantic import BaseModel, Field


# --- Supervisor Schemas ---
class InvestigationStep(BaseModel):
    agent_name: Literal["LogTraceAnalystAgent", "DatabaseInfraAgent", "RunbookKnowledgeAgent"]
    reasoning: str = Field(description="Por que este agente precisa ser acionado.")
    input_directive: str = Field(
        description="Diretriz cirúrgica de pesquisa para o agente (máximo 200 caracteres)."
    )


class SupervisorDecision(BaseModel):
    incident_severity: Literal["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
    is_investigation_complete: bool = Field(
        description="True se a causa raiz foi comprovada ou se o orçamento de turnos esgotou."
    )
    next_steps: list[InvestigationStep] = Field(
        default_factory=list,
        description="Lista de passos para execução paralela ou sequencial.",
    )
    root_cause_hypothesis: str | None = Field(
        default=None, description="Hipótese primária da causa raiz quando identificada."
    )


# --- Log Analyst Schemas ---
class LogAnomaly(BaseModel):
    error_pattern: str
    frequency: int
    first_seen: str
    last_seen: str
    sample_message: str


class LogAnalysisResult(BaseModel):
    found_anomalies: list[LogAnomaly] = Field(default_factory=list)
    probable_origin_service: str
    error_spike_percentage: float
    summary: str


# --- Database & Infra Analyst Schemas ---
class InfraAnalysisResult(BaseModel):
    database_pool_utilization_pct: float
    active_long_running_queries: int
    pod_restart_count: int
    is_resource_exhausted: bool
    diagnostic_evidence: str


# --- Runbook Knowledge (RAG) Schemas ---
class RunbookRecommendation(BaseModel):
    runbook_title: str
    section: str
    recommended_procedure: str
    source_file: str
    confidence_score: float


class RunbookRetrievalResult(BaseModel):
    recommendations: list[RunbookRecommendation] = Field(default_factory=list)
    synthesis: str


# --- Remediation Engineer Schemas ---
class RemediationPlan(BaseModel):
    action_type: Literal[
        "DATABASE_CONNECTION_SCALE",
        "DATABASE_TERMINATE_BACKENDS",
        "POD_ROLLOUT_RESTART",
        "CONFIG_ROLLBACK",
        "TRAFFIC_DRAIN",
        "CIRCUIT_BREAKER_ACTIVATE",
        "SCHEMA_HOTFIX",
    ]
    is_critical_action: bool = Field(
        default=True,
        description="True se exigir portão HITL obrigatório antes da execução.",
    )
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    proposed_commands: list[str] = Field(description="Comandos exatos a serem executados.")
    patch_diff: str | None = Field(
        default=None,
        description="Diff unificado (git patch ou yaml diff) da alteração proposta.",
    )
    rollback_plan: str = Field(
        description="Procedimento exato para desfazer a ação caso o problema se agrave."
    )
    justification: str = Field(
        description="Racional técnico de por que esta ação resolve a causa raiz."
    )


# --- Audit & Post-Mortem Schemas ---
class TimelineEvent(BaseModel):
    timestamp: str
    event_type: Literal[
        "ALERT_INGESTED",
        "INVESTIGATION_STARTED",
        "ROOT_CAUSE_IDENTIFIED",
        "PLAN_PROPOSED",
        "HUMAN_APPROVED",
        "ACTION_EXECUTED",
        "INCIDENT_RESOLVED",
    ]
    description: str
    actor: str


class PreventativeAction(BaseModel):
    title: str
    action_item: str
    owner_team: str
    priority: Literal["P0", "P1", "P2"]


class PostMortemReport(BaseModel):
    incident_id: str
    incident_title: str
    severity: Literal["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
    total_duration_minutes: float
    estimated_cost_avoided_usd: float
    root_cause_analysis: str
    timeline: list[TimelineEvent] = Field(default_factory=list)
    mitigation_applied: str
    rollback_instructions: str
    preventative_actions: list[PreventativeAction] = Field(default_factory=list)
    human_signoff_by: str
    signoff_timestamp: str
    cryptographic_audit_hash: str


# --- Webhook & API Schemas ---
class IncidentWebhookPayload(BaseModel):
    source: Literal["datadog", "prometheus", "grafana", "pagerduty", "manual", "chaos_studio"] = (
        "datadog"
    )
    title: str = "Incident Alert"
    severity: Literal["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"] = "P1_HIGH"
    service: str
    description: str = ""
    message: str | None = None
    details: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    raw_logs: list[str] = Field(default_factory=list)


class ResumeIncidentPayload(BaseModel):
    approved: bool = True
    human_approved: bool | None = None
    approved_by: str = Field(description="E-mail ou ID do engenheiro autorizador.")
    override_commands: list[str] | None = Field(
        default=None, description="Comandos alternativos caso o engenheiro ajuste o plano."
    )
    operator_notes: str | None = None

    @property
    def is_approved(self) -> bool:
        if self.human_approved is not None:
            return self.human_approved
        return self.approved


class IncidentResponse(BaseModel):
    incident_id: str
    status: str
    severity: str
    message: str = ""
    service: str | None = None
    created_at: str | None = None
    root_cause_summary: str | None = None
    remediation_plan: dict | None = None
    retrieved_sources: list[str] = Field(default_factory=list)
    total_tokens_consumed: int = 0
    is_budget_exceeded: bool = False
    agent_results: dict = Field(default_factory=dict)
    human_approved: bool | None = None
    approved_by: str | None = None
    approval_timestamp: str | None = None


# Aliases for API compatibility
AlertPayload = IncidentWebhookPayload
ResumeIncidentRequest = ResumeIncidentPayload

__all__ = [
    "InvestigationStep",
    "SupervisorDecision",
    "LogAnomaly",
    "LogAnalysisResult",
    "InfraAnalysisResult",
    "RunbookRecommendation",
    "RunbookRetrievalResult",
    "RemediationPlan",
    "TimelineEvent",
    "PreventativeAction",
    "PostMortemReport",
    "IncidentWebhookPayload",
    "AlertPayload",
    "ResumeIncidentPayload",
    "ResumeIncidentRequest",
    "IncidentResponse",
]
