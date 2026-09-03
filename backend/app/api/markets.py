"""
Market API — Prices, Trends, Forecasts, Markets list
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.agents.orchestrator import get_orchestrator
from app.api.deps import get_current_user
from app.models.models import User
from app.services.market_data_provider import DEMO_MARKETS, DEMO_CROPS

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("")
async def list_markets(district: Optional[str] = Query(None)):
    orch = get_orchestrator()
    markets = await orch.market_provider.get_market_list(district)
    return {"markets": markets, "is_demo": True}


@router.get("/crops")
async def list_crops():
    return {
        "crops": [
            {"id": k, **v} for k, v in DEMO_CROPS.items()
        ]
    }


@router.get("/prices")
async def get_prices(
    crop_id: str = Query("crop_cotton"),
    market_id: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
):
    orch = get_orchestrator()
    mandi_result = await orch.mandi_agent._timed_run(
        crop_id=crop_id, market_id=market_id, district=district, quantity=1
    )
    if not mandi_result.success:
        return {"error": mandi_result.error, "is_demo": True}
    return mandi_result.data


@router.get("/prices/trend")
async def get_price_trend(
    crop_id: str = Query("crop_cotton"),
    market_id: str = Query("mkt_ahmedabad"),
    days: int = Query(30, ge=7, le=90),
):
    orch = get_orchestrator()
    history = await orch.market_provider.get_historical_prices(crop_id, market_id, days)
    return {
        "crop_id": crop_id,
        "market_id": market_id,
        "days": days,
        "prices": [
            {"date": h.price_date.isoformat()[:10], "min": float(h.min_price), "max": float(h.max_price), "modal": float(h.modal_price)}
            for h in history
        ],
        "is_demo": True,
        "source": "demo_data",
        "note": "DEMO DATA — not live market prices",
    }


@router.get("/prices/forecast")
async def get_forecast(
    crop_id: str = Query("crop_cotton"),
    market_id: str = Query("mkt_ahmedabad"),
):
    orch = get_orchestrator()
    forecast_result = await orch.forecast_agent._timed_run(
        crop_id=crop_id, market_id=market_id, horizon_days=7
    )
    if not forecast_result.success:
        return {"error": forecast_result.error}
    return {**forecast_result.data, "is_demo": True}
