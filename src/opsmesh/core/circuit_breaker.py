"""OpsMesh FinOps Circuit Breaker Module (Anti-Denial-of-Wallet)."""

import threading
from datetime import UTC, datetime

from opsmesh.core.config import settings


class DailyTokenCircuitBreaker:
    """Controlador de gastos e consumo de tokens diário."""

    def __init__(self, token_limit: int | None = None, budget_usd: float | None = None):
        self._lock = threading.Lock()
        self.token_limit = token_limit or settings.FINOPS_DAILY_TOKEN_LIMIT
        self.budget_usd = budget_usd or settings.FINOPS_DAILY_BUDGET_USD
        self.current_day_utc = datetime.now(UTC).date()
        self.total_tokens_consumed_today = 0
        self.total_cost_usd_today = 0.0

    def _reset_if_new_day(self) -> None:
        """Reinicia o contador se virar o dia em UTC."""
        today = datetime.now(UTC).date()
        if today > self.current_day_utc:
            self.current_day_utc = today
            self.total_tokens_consumed_today = 0
            self.total_cost_usd_today = 0.0

    def check_allowed(self, is_byok: bool = False) -> tuple[bool, str]:
        """Verifica se a requisição pode ser processada.

        Se o usuário fornecer chave própria (BYOK), a cota pública é ignorada.
        """
        if is_byok:
            return True, "BYOK autorizada sem consumo da cota do servidor."

        with self._lock:
            self._reset_if_new_day()
            if self.total_tokens_consumed_today >= self.token_limit:
                return (
                    False,
                    f"Cota diária de demonstração pública atingida ({self.total_tokens_consumed_today}/{self.token_limit} tokens). "
                    "Ela é reiniciada às 00:00 UTC. Para continuar agora, use o header 'X-OpenAI-API-Key' / 'X-DeepSeek-API-Key' ou execute localmente.",
                )
            return True, "OK"

    def record_consumption(
        self, tokens: int, estimated_cost_usd: float = 0.0, is_byok: bool = False
    ) -> None:
        """Registra consumo de tokens do dia."""
        if is_byok:
            return  # Não contabiliza no saldo do mantenedor

        with self._lock:
            self._reset_if_new_day()
            self.total_tokens_consumed_today += tokens
            self.total_cost_usd_today += estimated_cost_usd

    def get_status(self) -> dict:
        """Retorna telemetria atual do disjuntor."""
        with self._lock:
            self._reset_if_new_day()
            return {
                "date_utc": str(self.current_day_utc),
                "tokens_consumed_today": self.total_tokens_consumed_today,
                "token_limit": self.token_limit,
                "estimated_cost_usd_today": round(self.total_cost_usd_today, 4),
                "budget_limit_usd": self.budget_usd,
                "is_tripped": self.total_tokens_consumed_today >= self.token_limit,
            }


circuit_breaker = DailyTokenCircuitBreaker()
