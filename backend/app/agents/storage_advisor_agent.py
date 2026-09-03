"""
Agent 3: Storage & Selling Timing Advisor Agent
Deterministic economic decision engine — never uses LLM for calculations.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

from app.agents.base import BaseAgent, AgentResult
from app.core.logging import logger


# Quality loss rates per crop per day (conservative estimates)
QUALITY_LOSS_RATE: Dict[str, float] = {
    "crop_cotton": 0.0008,      # 0.08%/day
    "crop_groundnut": 0.0015,   # 0.15%/day — higher moisture risk
}

# Minimum price change % to justify storage
MIN_GAIN_THRESHOLD = 0.005  # 0.5% net gain minimum to recommend storage


class StorageAdvisorAgent(BaseAgent):
    name = "StorageAdvisorAgent"

    async def run(
        self,
        crop_id: str,
        quantity: float,
        current_price: float,
        forecast_price: float,
        forecast_confidence: float,
        storage_available: bool,
        storage_cost_per_quintal_per_day: float,
        transport_cost_total: float,
        horizon_days: int,
        **kwargs,
    ) -> AgentResult:
        logger.info("StorageAdvisorAgent running", crop_id=crop_id, quantity=quantity)

        # ── Revenue calculations ────────────────────────────────
        current_revenue = round(current_price * quantity, 2)
        expected_future_gross = round(forecast_price * quantity, 2)

        storage_cost = round(
            storage_cost_per_quintal_per_day * quantity * horizon_days, 2
        ) if storage_available else round(quantity * horizon_days * 1.5, 2)  # warehouse estimate

        ql_rate = QUALITY_LOSS_RATE.get(crop_id, 0.001)
        quality_loss_pct = ql_rate * horizon_days
        quality_loss_cost = round(quality_loss_pct * expected_future_gross, 2)

        expected_net_revenue = round(
            expected_future_gross - storage_cost - transport_cost_total - quality_loss_cost, 2
        )

        potential_gain = round(expected_net_revenue - current_revenue, 2)

        # ── Decision logic ──────────────────────────────────────
        price_change_pct = (forecast_price - current_price) / current_price if current_price > 0 else 0
        net_gain_pct = potential_gain / current_revenue if current_revenue > 0 else 0

        # Adjust confidence down if forecast confidence is low
        decision_confidence = round(forecast_confidence * 0.9, 3)

        if net_gain_pct >= MIN_GAIN_THRESHOLD and price_change_pct > 0:
            if forecast_confidence >= 0.70:
                action = "STORE"
            else:
                action = "WAIT"
        elif net_gain_pct < 0:
            action = "SELL_NOW"
        elif price_change_pct < 0:
            action = "SELL_NOW"
        else:
            action = "WAIT"

        # Recommended days: horizon, capped at 30
        recommended_days = horizon_days if action == "STORE" else None

        reasoning = self._build_reasoning(
            action, current_price, forecast_price, current_revenue,
            expected_net_revenue, storage_cost, quality_loss_cost,
            transport_cost_total, potential_gain, horizon_days,
            forecast_confidence, price_change_pct
        )

        return AgentResult(self.name, True, {
            "action": action,
            "recommended_days": recommended_days,
            "current_price": current_price,
            "current_revenue": current_revenue,
            "forecast_price": forecast_price,
            "expected_future_gross": expected_future_gross,
            "storage_cost": storage_cost,
            "transport_cost": transport_cost_total,
            "quality_loss_cost": quality_loss_cost,
            "expected_net_revenue": expected_net_revenue,
            "potential_gain": potential_gain,
            "price_change_pct": round(price_change_pct * 100, 2),
            "net_gain_pct": round(net_gain_pct * 100, 2),
            "confidence": decision_confidence,
            "reasoning": reasoning,
        })

    def _build_reasoning(self, action, cur, fut, cur_rev, net_rev,
                         stor, ql, trans, gain, days, fc_conf, pct_chg) -> str:
        if action == "STORE":
            return (
                f"Price forecast suggests a {pct_chg*100:.1f}% increase over {days} days "
                f"(₹{cur:,.0f} → ₹{fut:,.0f}/quintal). "
                f"After storage cost (₹{stor:,.0f}), transport (₹{trans:,.0f}), "
                f"and quality loss (₹{ql:,.0f}), expected net gain is ₹{gain:,.0f}. "
                f"Forecast confidence: {fc_conf*100:.0f}%."
            )
        elif action == "SELL_NOW":
            if gain < 0:
                return (
                    f"Storage and holding costs (₹{stor+trans+ql:,.0f}) exceed the expected "
                    f"price increase of ₹{(fut-cur)*1:,.0f}/quintal. "
                    f"Selling now at ₹{cur:,.0f}/quintal is more profitable by ₹{abs(gain):,.0f}."
                )
            else:
                return (
                    f"Current price of ₹{cur:,.0f}/quintal is favorable. "
                    f"No significant price increase expected. Selling now maximizes certainty."
                )
        else:  # WAIT
            return (
                f"Price may increase slightly, but forecast confidence ({fc_conf*100:.0f}%) "
                f"is below threshold. Monitor prices for 2-3 days before deciding. "
                f"Current price: ₹{cur:,.0f}/quintal."
            )
