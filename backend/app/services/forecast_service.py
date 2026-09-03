"""
KhedutMitra AI — Forecasting Service Abstraction

Uses deterministic baseline forecasting for the MVP.
Architecture supports hot-swapping in advanced ML/ARIMA/Prophet models.
"""
from __future__ import annotations
import abc
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from app.services.market_data_provider import MarketDataProvider


# ─────────────────────── Data Classes ─────────────────────────

class ForecastResult:
    def __init__(self, crop_id: str, market_id: str, horizon_days: int,
                 predicted_price: float, lower_bound: float, upper_bound: float,
                 confidence: float, model_version: str, factors: str, is_demo: bool):
        self.crop_id = crop_id
        self.market_id = market_id
        self.horizon_days = horizon_days
        self.target_date = (datetime.utcnow() + timedelta(days=horizon_days)).isoformat()[:10]
        self.predicted_price = predicted_price
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.confidence = confidence
        self.model_version = model_version
        self.factors = factors
        self.is_demo = is_demo
        self.disclaimer = "Forecasts are estimates based on historical patterns. Actual market prices may differ significantly."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "crop_id": self.crop_id,
            "market_id": self.market_id,
            "horizon_days": self.horizon_days,
            "target_date": self.target_date,
            "predicted_price": self.predicted_price,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "confidence": self.confidence,
            "model_version": self.model_version,
            "factors": self.factors,
            "is_demo": self.is_demo,
            "disclaimer": self.disclaimer,
        }


# ─────────────────────── Abstract Base ────────────────────────

class ForecastModel(abc.ABC):
    model_version: str = "abstract_v0"

    @abc.abstractmethod
    async def forecast(self, crop_id: str, market_id: str, horizon_days: int,
                       historical_prices: List[float]) -> ForecastResult:
        ...


# ─────────────────────── Baseline Model ───────────────────────

class BaselineForecastModel(ForecastModel):
    """
    Weighted moving average + trend + seasonality.
    Confidence degrades with forecast horizon.
    """
    model_version = "baseline_v1"

    async def forecast(self, crop_id: str, market_id: str, horizon_days: int,
                       historical_prices: List[float]) -> ForecastResult:
        if not historical_prices:
            raise ValueError("No historical prices available for forecasting")

        prices = historical_prices[-30:] if len(historical_prices) >= 30 else historical_prices
        n = len(prices)

        # Weighted moving average: recent days weighted higher
        weights = [i + 1 for i in range(n)]
        wma = sum(p * w for p, w in zip(prices, weights)) / sum(weights)

        # Linear trend from last 14 days
        recent = prices[-14:] if n >= 14 else prices
        if len(recent) >= 2:
            trend_per_day = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
        else:
            trend_per_day = 0.0

        # Mild seasonal boost for cotton harvest season (Oct-Feb) / groundnut (Sep-Jan)
        month = datetime.utcnow().month
        seasonal_factor = 1.0
        if crop_id == "crop_cotton" and month in (10, 11, 12, 1):
            seasonal_factor = 1.015
        elif crop_id == "crop_groundnut" and month in (9, 10, 11, 12):
            seasonal_factor = 1.012

        # Volatility from price std dev
        mean_p = sum(prices) / len(prices)
        variance = sum((p - mean_p) ** 2 for p in prices) / len(prices)
        std_dev = math.sqrt(variance)
        vol_pct = std_dev / mean_p if mean_p > 0 else 0.02

        predicted = (wma + trend_per_day * horizon_days) * seasonal_factor
        predicted = max(predicted, mean_p * 0.8)  # sanity floor

        # Uncertainty band widens with horizon
        band_pct = vol_pct * math.sqrt(horizon_days)
        lower = round(predicted * (1 - band_pct), 2)
        upper = round(predicted * (1 + band_pct), 2)
        predicted = round(predicted, 2)

        # Confidence decreases with horizon
        base_confidence = 0.85
        confidence = round(max(0.35, base_confidence - 0.035 * horizon_days + 0.005 * min(n, 30)), 3)

        trend_dir = "upward" if trend_per_day > 0 else "downward" if trend_per_day < 0 else "stable"
        factors = (
            f"Weighted moving average of {n} data points; "
            f"trend={trend_dir} ({trend_per_day:+.1f} ₹/day); "
            f"seasonal_factor={seasonal_factor:.3f}; "
            f"volatility={vol_pct*100:.1f}%"
        )

        return ForecastResult(
            crop_id=crop_id, market_id=market_id, horizon_days=horizon_days,
            predicted_price=predicted, lower_bound=lower, upper_bound=upper,
            confidence=confidence, model_version=self.model_version,
            factors=factors, is_demo=True,
        )


# ─────────────────────── Forecast Service ─────────────────────

class ForecastService:
    """Orchestrates forecast generation using the registered model."""

    DEFAULT_HORIZONS = [3, 7, 15, 30]

    def __init__(self, market_provider: MarketDataProvider, model: Optional[ForecastModel] = None):
        self.market_provider = market_provider
        self.model = model or BaselineForecastModel()

    async def forecast_series(self, crop_id: str, market_id: str,
                              horizons: Optional[List[int]] = None) -> List[ForecastResult]:
        horizons = horizons or self.DEFAULT_HORIZONS
        history = await self.market_provider.get_historical_prices(crop_id, market_id, days=60)
        prices = [float(p.modal_price) for p in history]
        results = []
        for h in horizons:
            result = await self.model.forecast(crop_id, market_id, h, prices)
            results.append(result)
        return results

    async def forecast_single(self, crop_id: str, market_id: str, horizon_days: int) -> ForecastResult:
        history = await self.market_provider.get_historical_prices(crop_id, market_id, days=60)
        prices = [float(p.modal_price) for p in history]
        return await self.model.forecast(crop_id, market_id, horizon_days, prices)
