"""
Agent 6: Farmer Income Dashboard Agent
Aggregates inventory, prices, forecasts, recommendations into an income summary.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent, AgentResult
from app.core.logging import logger


class IncomeDashboardAgent(BaseAgent):
    name = "IncomeDashboardAgent"

    async def run(
        self,
        farmer_name: str,
        district: Optional[str],
        inventory: List[Dict[str, Any]],
        price_data: Dict[str, Any],
        forecast_data: Dict[str, Any],
        buyer_matches: List[Dict[str, Any]],
        storage_recommendation: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AgentResult:
        logger.info("IncomeDashboardAgent running", farmer=farmer_name)

        cotton_qty = sum(i["quantity"] for i in inventory if "cotton" in i.get("crop_id", ""))
        groundnut_qty = sum(i["quantity"] for i in inventory if "groundnut" in i.get("crop_id", ""))
        total_qty = cotton_qty + groundnut_qty

        # Current estimated value
        current_price = price_data.get("current_price", 0)
        current_value = round(total_qty * current_price, 2)

        # Expected value based on 7d forecast
        forecast_price_7d = forecast_data.get("predicted_price", current_price)
        expected_value = round(total_qty * forecast_price_7d, 2)

        # Potential gain from waiting
        potential_gain = round(expected_value - current_value, 2)
        if storage_recommendation:
            potential_gain = storage_recommendation.get("potential_gain", potential_gain)

        # Active buyer opportunities
        active_buyers = len([m for m in buyer_matches if m.get("match_score", 0) >= 60])

        # Revenue scenarios
        scenarios = []
        for horizon, label in [(0, "Sell Now"), (7, "Store 7 Days"), (15, "Store 15 Days")]:
            if horizon == 0:
                rev = round(total_qty * current_price, 2)
                net = rev - 2000  # base transport
            else:
                fc_price = forecast_data.get("predicted_price", current_price)
                stor_cost = total_qty * 0.5 * horizon
                ql_cost = round(total_qty * fc_price * 0.001 * horizon, 2)
                rev = round(total_qty * fc_price, 2)
                net = round(rev - stor_cost - 2000 - ql_cost, 2)
            scenarios.append({
                "label": label,
                "gross_revenue": rev,
                "net_revenue": net,
                "horizon_days": horizon,
            })

        return AgentResult(self.name, True, {
            "farmer_name": farmer_name,
            "district": district,
            "total_inventory_quintals": total_qty,
            "cotton_quintals": cotton_qty,
            "groundnut_quintals": groundnut_qty,
            "current_price": current_price,
            "current_estimated_value": current_value,
            "forecast_price_7d": forecast_price_7d,
            "expected_value_7d": expected_value,
            "potential_gain": max(0.0, potential_gain),
            "active_buyer_opportunities": active_buyers,
            "revenue_scenarios": scenarios,
            "recommendation_action": storage_recommendation.get("action") if storage_recommendation else "SELL_NOW",
            "top_buyers": buyer_matches[:3],
        })
