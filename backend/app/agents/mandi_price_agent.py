"""
Agent 1: Mandi Price Intelligence Agent
Retrieves, normalizes, and analyzes current + historical market prices.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent, AgentResult
from app.services.market_data_provider import MarketDataProvider
from app.core.logging import logger


class MandiPriceAgent(BaseAgent):
    name = "MandiPriceAgent"

    def __init__(self, market_provider: MarketDataProvider):
        self.market_provider = market_provider

    async def run(self, crop_id: str, market_id: Optional[str] = None,
                  district: Optional[str] = None, quantity: float = 1.0,
                  **kwargs) -> AgentResult:
        logger.info("MandiPriceAgent running", crop_id=crop_id, market_id=market_id)

        # Get current prices across all/selected markets
        current = await self.market_provider.get_current_prices(crop_id, market_id)
        if not current:
            return AgentResult(self.name, False, {}, "No market price data available")

        # If no specific market, find closest to district
        if market_id is None and district:
            district_lower = district.lower()
            district_match = [p for p in current if district_lower in p.market_name.lower() or district_lower in p.market_id.lower()]
            if district_match:
                current = district_match

        # Determine primary market (highest arrivals = most liquid)
        primary = max(current, key=lambda p: p.arrivals_tonnes or 0)

        # Historical data for trend
        history = await self.market_provider.get_historical_prices(primary.market_id, crop_id, days=14)
        modals = [float(h.modal_price) for h in history]

        if len(modals) >= 2:
            trend_pct = ((modals[-1] - modals[0]) / modals[0]) * 100
            trend = "upward" if trend_pct > 0.5 else "downward" if trend_pct < -0.5 else "stable"
        else:
            trend_pct = 0.0
            trend = "stable"

        all_modals = [float(p.modal_price) for p in current]
        avg_price = sum(all_modals) / len(all_modals)
        max_market = max(current, key=lambda p: float(p.modal_price))

        # Anomaly: price > 10% from average
        anomaly = abs(float(primary.modal_price) - avg_price) / avg_price > 0.10

        # Price per quintal (current)
        current_revenue = float(primary.modal_price) * quantity

        nearby_mandis = [
            {
                "market_id": p.market_id,
                "market_name": p.market_name,
                "modal_price": float(p.modal_price),
                "min_price": float(p.min_price),
                "max_price": float(p.max_price),
                "arrivals_tonnes": p.arrivals_tonnes,
            }
            for p in sorted(current, key=lambda x: float(x.modal_price), reverse=True)[:5]
        ]

        return AgentResult(self.name, True, {
            "crop_id": crop_id,
            "crop_name": primary.crop_name,
            "primary_market_id": primary.market_id,
            "primary_market_name": primary.market_name,
            "current_price": float(primary.modal_price),
            "min_price": float(primary.min_price),
            "max_price": float(primary.max_price),
            "avg_price_across_mandis": round(avg_price, 2),
            "best_market_name": max_market.market_name,
            "best_market_price": float(max_market.modal_price),
            "trend": trend,
            "trend_percentage": round(trend_pct, 2),
            "data_timestamp": primary.price_date.isoformat(),
            "source": primary.source,
            "confidence": 0.90 if not anomaly else 0.75,
            "current_revenue": round(current_revenue, 2),
            "nearby_mandis": nearby_mandis,
            "price_history_14d": [
                {"date": h.price_date.isoformat()[:10], "price": float(h.modal_price)}
                for h in history
            ],
            "is_demo": primary.is_demo,
            "anomaly_detected": anomaly,
        })
