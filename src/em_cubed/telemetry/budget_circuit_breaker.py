"""Budget circuit breaker for automatic cost threshold enforcement and model fallback steering."""

from enum import Enum
from typing import Any
import structlog

logger = structlog.get_logger()


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Budget limit reached; execution blocked or fallback triggered


class BudgetCircuitBreaker:
    """Enforce dollar cost budgets per session/project with automatic fallback steering."""

    def __init__(self, max_budget_dollars: float = 10.0):
        self.max_budget_dollars = max_budget_dollars
        self.current_spend_dollars = 0.0
        self.state = CircuitState.CLOSED
        logger.info("BudgetCircuitBreaker initialized", max_budget=self.max_budget_dollars)

    def record_cost(self, cost_dollars: float) -> CircuitState:
        """Record an execution cost and update circuit breaker state.

        Args:
            cost_dollars: Estimated cost of execution in USD

        Returns:
            Current CircuitState (CLOSED or OPEN)
        """
        self.current_spend_dollars += max(0.0, cost_dollars)

        if self.current_spend_dollars >= self.max_budget_dollars:
            if self.state != CircuitState.OPEN:
                self.state = CircuitState.OPEN
                logger.warning(
                    "Budget limit reached! Circuit breaker opened.",
                    spend=self.current_spend_dollars,
                    limit=self.max_budget_dollars,
                )
        return self.state

    def check_execution_allowed(self, surface_name: str) -> dict[str, Any]:
        """Check if execution is allowed or if fallback is required."""
        if self.state == CircuitState.OPEN and surface_name in ("llm", "expensive"):
            return {
                "allowed": False,
                "reason": f"Budget circuit breaker is OPEN (${self.current_spend_dollars:.2f} / ${self.max_budget_dollars:.2f}).",
                "recommended_fallback": "python",
            }
        return {"allowed": True, "reason": "Spend within configured budget limits."}

    def reset(self) -> None:
        """Reset spend tracking and close circuit breaker."""
        self.current_spend_dollars = 0.0
        self.state = CircuitState.CLOSED
        logger.info("BudgetCircuitBreaker reset to CLOSED")
