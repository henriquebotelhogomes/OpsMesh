"""OpenRouter Gateway and Jev Decision Engine.

Provides native integration with OpenRouter API and the specialized Jev Decision Model
(typesafe/jev-latest) for sub-30ms, $0.00 output cost routing and convergence evaluation.
"""

from __future__ import annotations

import logging
from typing import Any

from openai import AsyncOpenAI

from opsmesh.core.config import settings
from opsmesh.core.schemas import InvestigationStep, SupervisorDecision

logger = logging.getLogger(__name__)

OPENROUTER_DEFAULT_REFERER = "https://opsmesh.local"
OPENROUTER_DEFAULT_TITLE = "OpsMesh Incident Commander"


class OpenRouterClient:
    """Client for OpenRouter LLM Gateway and Free Models Fleet."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = base_url or settings.OPENROUTER_BASE_URL
        self.default_model = default_model or settings.OPENROUTER_MODEL_NAME

        self._client: AsyncOpenAI | None = None
        if self.api_key:
            try:
                self._client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    default_headers={
                        "HTTP-Referer": OPENROUTER_DEFAULT_REFERER,
                        "X-Title": OPENROUTER_DEFAULT_TITLE,
                    },
                )
            except Exception as exc:
                logger.warning("Failed to initialize OpenRouter AsyncOpenAI client: %s", exc)

    @property
    def is_configured(self) -> bool:
        """Check if OpenRouter client is configured with an API key."""
        return self._client is not None and bool(self.api_key)

    async def complete_structured(
        self,
        messages: list[dict[str, str]],
        response_model: type[Any],
        model: str | None = None,
        temperature: float = 0.1,
    ) -> Any:
        """Execute structured JSON completion using OpenRouter model."""
        target_model = model or self.default_model
        if not self._client:
            raise RuntimeError("OpenRouter client is not configured with an API key.")

        response = await self._client.beta.chat.completions.parse(
            model=target_model,
            messages=messages,  # type: ignore[arg-type]
            response_format=response_model,
            temperature=temperature,
        )
        return response.choices[0].message.parsed


class JevDecisionEngine:
    """Decision Model Engine powered by Jev (typesafe/jev-latest) via OpenRouter.

    Specialized in categorical routing (Choice) and boolean convergence (Noul)
    with sub-30ms execution and zero output token cost.
    """

    def __init__(
        self,
        client: OpenRouterClient | None = None,
        jev_model: str | None = None,
    ) -> None:
        self.client = client or OpenRouterClient()
        self.jev_model = jev_model or settings.JEV_MODEL_NAME

    async def evaluate_convergence_and_routing(
        self,
        severity: str,
        iteration_count: int,
        max_iterations: int,
        alert_description: str,
        agent_results: dict[str, Any],
    ) -> SupervisorDecision:
        """Evaluate if root cause has converged or choose next diagnostic specialist."""
        # Hard limits check
        if iteration_count >= max_iterations:
            return SupervisorDecision(
                incident_severity=severity,  # type: ignore[arg-type]
                is_investigation_complete=True,
                next_steps=[],
                root_cause_hypothesis=f"Convergência forçada por limite de turnos ({iteration_count}/{max_iterations}).",
            )

        # If OpenRouter is configured with Jev, attempt sub-30ms decision
        if self.client.is_configured:
            try:
                system_prompt = (
                    "Você é o Decision Model Jev para o OpsMesh. Avalie se as evidências técnicas "
                    "são suficientes para comprovar a causa raiz (is_investigation_complete=True) "
                    "ou selecione cirurgicamente os especialistas necessários: "
                    "['LogTraceAnalystAgent', 'DatabaseInfraAgent', 'RunbookKnowledgeAgent']."
                )
                user_prompt = (
                    f"Turno: {iteration_count}/{max_iterations}\n"
                    f"Alerta: {alert_description}\n"
                    f"Evidências coletadas: {agent_results}"
                )
                decision = await self.client.complete_structured(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_model=SupervisorDecision,
                    model=self.jev_model,
                    temperature=0.0,
                )
                if decision:
                    return decision
            except Exception as exc:
                logger.info("Jev decision fallback: %s. Using deterministic choice.", exc)

        # Deterministic Choice & Noul logic
        has_log = "LogTraceAnalystAgent" in agent_results
        has_infra = "DatabaseInfraAgent" in agent_results

        if not agent_results:
            # Initial Turn: Dispatch parallel specialists
            return SupervisorDecision(
                incident_severity=severity,  # type: ignore[arg-type]
                is_investigation_complete=False,
                next_steps=[
                    InvestigationStep(
                        agent_name="LogTraceAnalystAgent",
                        reasoning="Verificar stack traces e anomalias de erros no serviço.",
                        input_directive=f"Analisar erros para: {alert_description[:180]}",
                    ),
                    InvestigationStep(
                        agent_name="DatabaseInfraAgent",
                        reasoning="Inspecionar métricas de pool de conexões e pods.",
                        input_directive="Verificar conexões e pods",
                    ),
                    InvestigationStep(
                        agent_name="RunbookKnowledgeAgent",
                        reasoning="Recuperar runbooks corporativos relevantes.",
                        input_directive=f"Runbooks para: {alert_description[:180]}",
                    ),
                ],
                root_cause_hypothesis=None,
            )

        # If specialists responded, converge
        evidence_parts = []
        if has_log:
            log_data = agent_results["LogTraceAnalystAgent"]
            if isinstance(log_data, dict) and log_data.get("summary"):
                evidence_parts.append(str(log_data["summary"]))
        if has_infra:
            infra_data = agent_results["DatabaseInfraAgent"]
            if isinstance(infra_data, dict) and infra_data.get("diagnostic_evidence"):
                evidence_parts.append(str(infra_data["diagnostic_evidence"]))

        hypothesis = " | ".join(evidence_parts) if evidence_parts else alert_description[:200]
        return SupervisorDecision(
            incident_severity=severity,  # type: ignore[arg-type]
            is_investigation_complete=True,
            next_steps=[],
            root_cause_hypothesis=hypothesis,
        )
