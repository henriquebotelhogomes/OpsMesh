"""IncidentSupervisorAgent (Incident Commander).

Orchestrates multi-agent crisis investigation, plans parallel diagnostics,
and strictly enforces iteration turn limits (max 4 turns) and token budgets.
"""

from __future__ import annotations

import logging
from typing import Any

from openai import AsyncOpenAI

from opsmesh.core.config import settings
from opsmesh.core.schemas import InvestigationStep, SupervisorDecision
from opsmesh.core.state import IncidentState

logger = logging.getLogger(__name__)

SUPERVISOR_SYSTEM_PROMPT = """Você é o IncidentSupervisorAgent, o Comandante de Incidentes de nível Staff SRE do OpsMesh.
Sua missão é liderar a resolução de crises em sistemas distribuídos de missão crítica, minimizando o MTTR com segurança absoluta.

DIRETRIZES FUNDAMENTAIS:
1. Você recebe alertas onde todo dado sensível (PII, senhas, tokens) já foi mascarado por governança de privacidade. IPs de redes privadas RFC 1918 e hostnames de Pods K8s foram preservados para diagnóstico.
2. Analise a anomalia descrita e planeje a investigação cirúrgica acionando seus especialistas:
   - LogTraceAnalystAgent para correlações de logs, stack traces e anomalias de erros.
   - DatabaseInfraAgent para checar conexões de banco, queries lentas, locks e pods K8s.
   - RunbookKnowledgeAgent para recuperar os procedimentos operacionais padrão (SOPs).
3. Não faça suposições sem evidências técnicas auditáveis.
4. Mantenha as diretivas de pesquisa concisas para economizar tokens (máximo 200 caracteres por diretiva).
5. Quando as evidências convergirem para uma causa raiz comprovada ou o limite de turnos esgotar, marque is_investigation_complete=True.
6. Comunique-se em Português técnico, claro e conciso."""


class IncidentSupervisorAgent:
    """Incident Commander orchestrator enforcing token budgets and iteration limits."""

    def __init__(
        self, api_key: str | None = None, base_url: str | None = None, model: str | None = None
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or (
            settings.DEEPSEEK_BASE_URL if settings.DEEPSEEK_API_KEY else None
        )
        self.model_name = model or (
            "deepseek-chat" if settings.DEEPSEEK_API_KEY else settings.OPENAI_MODEL_NAME
        )
        self._client: AsyncOpenAI | None = None
        if self.api_key:
            try:
                self._client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            except Exception as exc:
                logger.warning("Could not initialize AsyncOpenAI client: %s", exc)

    async def decide(self, state: IncidentState) -> SupervisorDecision:
        """Decide next investigation steps or conclude root-cause analysis."""
        iteration_count = state.get("iteration_count", 1)
        max_iterations = state.get("max_iterations", 4)
        is_budget_exceeded = state.get("is_budget_exceeded", False)
        agent_results = state.get("agent_results", {}) or {}
        raw_alert = state.get("raw_alert_sanitized", {}) or {}
        alert_desc = str(raw_alert.get("description") or raw_alert.get("message") or raw_alert)

        # FinOps & Turn Guardrail: Hard trip on max iterations or budget
        if iteration_count >= max_iterations or is_budget_exceeded:
            logger.info(
                "Supervisor reached limit (iteration=%d/%d, budget_exceeded=%s). Forcing completion.",
                iteration_count,
                max_iterations,
                is_budget_exceeded,
            )
            return SupervisorDecision(
                incident_severity=state.get("severity", "P1_HIGH"),
                is_investigation_complete=True,
                next_steps=[],
                root_cause_hypothesis=self._build_fallback_hypothesis(agent_results, alert_desc),
            )

        # If LLM client is configured, run structured completion
        if self._client:
            try:
                prompt_content = (
                    f"Incidente: {state.get('incident_id')}\n"
                    f"Turno: {iteration_count}/{max_iterations}\n"
                    f"Alerta Sanitizado: {raw_alert}\n"
                    f"Resultados de Especialistas até agora: {agent_results}"
                )
                response = await self._client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt_content},
                    ],
                    response_format=SupervisorDecision,
                    temperature=0.1,
                )
                parsed = response.choices[0].message.parsed
                if parsed:
                    return parsed
            except Exception as exc:
                logger.warning(
                    "LLM completion failed, falling back to deterministic decision logic: %s", exc
                )

        # Deterministic logic for Replay / Offline / Initial turn
        if not agent_results:
            # First turn: delegate to specialists
            return SupervisorDecision(
                incident_severity=state.get("severity", "P1_HIGH"),
                is_investigation_complete=False,
                next_steps=[
                    InvestigationStep(
                        agent_name="LogTraceAnalystAgent",
                        reasoning="Buscar stack traces e padrões de falha nos logs recentes do serviço.",
                        input_directive=f"Buscar erros correlacionados ao alerta: {alert_desc[:180]}",
                    ),
                    InvestigationStep(
                        agent_name="DatabaseInfraAgent",
                        reasoning="Verificar saturação de conexões de banco e estado de pods do Kubernetes.",
                        input_directive="Inspecionar conexões ativas, pool e status dos pods.",
                    ),
                    InvestigationStep(
                        agent_name="RunbookKnowledgeAgent",
                        reasoning="Recuperar procedimentos operacionais padrão (SOPs) correlacionados.",
                        input_directive=f"Buscar runbooks para: {alert_desc[:180]}",
                    ),
                ],
                root_cause_hypothesis=None,
            )
        else:
            # Specialist results collected: converge to completion
            return SupervisorDecision(
                incident_severity=state.get("severity", "P1_HIGH"),
                is_investigation_complete=True,
                next_steps=[],
                root_cause_hypothesis=self._build_fallback_hypothesis(agent_results, alert_desc),
            )

    def _build_fallback_hypothesis(self, agent_results: dict[str, Any], alert_desc: str) -> str:
        """Synthesize a technical root cause hypothesis from collected agent evidence."""
        log_res = agent_results.get("LogTraceAnalystAgent", {})
        infra_res = agent_results.get("DatabaseInfraAgent", {})

        parts = []
        if isinstance(log_res, dict) and log_res.get("summary"):
            parts.append(f"Logs: {log_res['summary']}")
        if isinstance(infra_res, dict) and infra_res.get("diagnostic_evidence"):
            parts.append(f"Infra: {infra_res['diagnostic_evidence']}")

        if parts:
            return " e ".join(parts)
        return (
            f"Causa raiz provável relacionada à degradação reportada no alerta: {alert_desc[:250]}"
        )
