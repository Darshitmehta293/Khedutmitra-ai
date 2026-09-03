"""
Agent 2: Mandi Price Forecasting Agent
Generates multi-horizon price forecasts using pluggable forecast models.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent, AgentResult
from app.services.forecast_service import ForecastService
from app.core.logging import logger


class ForecastingAgent(BaseAgent):
    name = "ForecastingAgent"

    def __init__(self, forecast_service: ForecastService):
        self.forecast_service = forecast_service

    async def run(self, crop_id: str, market_id: str, horizon_days: int = 7,
                  **kwargs) -> AgentResult:
        logger.info("ForecastingAgent running", crop_id=crop_id, market_id=market_id, horizon=horizon_days)

        try:
            # Primary forecast for requested horizon
            primary = await self.forecast_service.forecast_single(crop_id, market_id, horizon_days)

            # Full series for charting
            series = await self.forecast_service.forecast_series(crop_id, market_id)

            return AgentResult(self.name, True, {
                "crop_id": crop_id,
                "market_id": market_id,
                "horizon_days": horizon_days,
                "predicted_price": primary.predicted_price,
                "lower_bound": primary.lower_bound,
                "upper_bound": primary.upper_bound,
                "confidence": primary.confidence,
                "model_version": primary.model_version,
                "factors": primary.factors,
                "target_date": primary.target_date,
                "forecast_series": [f.to_dict() for f in series],
                "is_demo": primary.is_demo,
                "disclaimer": primary.disclaimer,
            })
        except Exception as e:
            logger.error("ForecastingAgent error", error=str(e))
            return AgentResult(self.name, False, {}, str(e))
