"""
KhedutMitra AI — Agent Orchestrator

Central coordinator. Routes user intent → specialized agents → Granite → response.
Multi-agent pipeline for SELL_OR_STORE decisions:
  MandiPriceAgent → ForecastingAgent → StorageAdvisorAgent →
  BuyerMatchingAgent → IncomeDashboardAgent → GraniteLLMService → response
"""
from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional, Tuple

from app.agents.base import AgentResult
from app.agents.mandi_price_agent import MandiPriceAgent
from app.agents.forecasting_agent import ForecastingAgent
from app.agents.storage_advisor_agent import StorageAdvisorAgent
from app.agents.buyer_matching_agent import BuyerMatchingAgent
from app.agents.quality_grading_agent import QualityGradingAgent
from app.agents.income_dashboard_agent import IncomeDashboardAgent
from app.services.market_data_provider import get_market_data_provider
from app.services.forecast_service import ForecastService
from app.services.quality_service import get_quality_provider
from app.services.granite_service import get_granite_service, detect_intent
from app.core.config import settings
from app.core.logging import logger


# ─────────────────────── Intent → Agent mapping ───────────────

INTENT_AGENTS = {
    "MARKET_PRICE": ["MandiPriceAgent"],
    "PRICE_FORECAST": ["MandiPriceAgent", "ForecastingAgent"],
    "SELL_OR_STORE": ["MandiPriceAgent", "ForecastingAgent", "StorageAdvisorAgent", "BuyerMatchingAgent", "IncomeDashboardAgent"],
    "FIND_BUYER": ["MandiPriceAgent", "BuyerMatchingAgent"],
    "QUALITY_CHECK": ["QualityGradingAgent"],
    "INCOME": ["MandiPriceAgent", "ForecastingAgent", "BuyerMatchingAgent", "IncomeDashboardAgent"],
    "GENERAL_CROP_QUERY": ["MandiPriceAgent"],
}


class AgentOrchestrator:
    """
    Central orchestrator. Each method runs the appropriate pipeline.
    All numerical calculations are performed in specialized agents.
    Granite is invoked last for natural-language explanation only.
    """

    def __init__(self):
        provider_type = settings.MARKET_DATA_PROVIDER
        self.market_provider = get_market_data_provider(provider_type)
        self.forecast_service = ForecastService(self.market_provider)
        quality_svc = get_quality_provider(settings.ENABLE_QUALITY_AI)

        self.mandi_agent = MandiPriceAgent(self.market_provider)
        self.forecast_agent = ForecastingAgent(self.forecast_service)
        self.storage_agent = StorageAdvisorAgent()
        self.buyer_agent = BuyerMatchingAgent()
        self.quality_agent = QualityGradingAgent(quality_svc)
        self.income_agent = IncomeDashboardAgent()
        self.granite = get_granite_service()

    # ─────────────────── Full Recommendation Pipeline ─────────

    async def get_full_recommendation(
        self,
        crop_id: str,
        quantity: float,
        quality_grade: str,
        district: str,
        storage_available: bool = False,
        storage_cost_per_quintal_per_day: float = 0.5,
        transport_cost_total: float = 2000.0,
        horizon_days: int = 7,
        farmer_name: str = "Farmer",
        language: str = "en",
        inventory_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        trace: List[Dict[str, Any]] = []

        # ── Agent 1: Mandi Price ───────────────────────────────
        mandi_result = await self.mandi_agent._timed_run(
            crop_id=crop_id, district=district, quantity=quantity
        )
        trace.append({**mandi_result.to_trace(), "label": "✓ Market Agent checked current prices"})
        if not mandi_result.success:
            return self._fallback_response("Market data unavailable", trace)

        primary_market_id = mandi_result.data.get("primary_market_id", "mkt_ahmedabad")
        current_price = mandi_result.data["current_price"]
        crop_name = mandi_result.data.get("crop_name", "Crop")

        # ── Agent 2: Forecast ──────────────────────────────────
        forecast_result = await self.forecast_agent._timed_run(
            crop_id=crop_id, market_id=primary_market_id, horizon_days=horizon_days
        )
        trace.append({**forecast_result.to_trace(), "label": f"✓ Forecast Agent generated {horizon_days}-day forecast"})
        if not forecast_result.success:
            forecast_price = current_price
            forecast_confidence = 0.5
        else:
            forecast_price = forecast_result.data["predicted_price"]
            forecast_confidence = forecast_result.data["confidence"]

        # ── Agent 3: Storage Advisor ───────────────────────────
        storage_result = await self.storage_agent._timed_run(
            crop_id=crop_id,
            quantity=quantity,
            current_price=current_price,
            forecast_price=forecast_price,
            forecast_confidence=forecast_confidence,
            storage_available=storage_available,
            storage_cost_per_quintal_per_day=storage_cost_per_quintal_per_day,
            transport_cost_total=transport_cost_total,
            horizon_days=horizon_days,
        )
        trace.append({**storage_result.to_trace(), "label": "✓ Storage Agent calculated economics"})

        # ── Agent 4: Buyer Matching ────────────────────────────
        buyer_result = await self.buyer_agent._timed_run(
            crop_id=crop_id,
            quantity=quantity,
            quality_grade=quality_grade,
            district=district,
            preferred_price=current_price,
        )
        trace.append({**buyer_result.to_trace(), "label": f"✓ Buyer Agent found {len(buyer_result.data.get('matches', []))} matching buyers"})

        # ── Agent 5: Income Dashboard ──────────────────────────
        income_result = await self.income_agent._timed_run(
            farmer_name=farmer_name,
            district=district,
            inventory=[{"crop_id": crop_id, "quantity": quantity}],
            price_data=mandi_result.data,
            forecast_data=forecast_result.data if forecast_result.success else {},
            buyer_matches=buyer_result.data.get("matches", []) if buyer_result.success else [],
            storage_recommendation=storage_result.data if storage_result.success else None,
        )
        trace.append({**income_result.to_trace(), "label": "✓ Income Agent compared revenue scenarios"})

        # ── Granite: Natural Language Explanation ──────────────
        rec_data = storage_result.data if storage_result.success else {}
        rec_data["crop_name"] = crop_name
        rec_data["quantity"] = quantity
        granite_explanation = await self.granite.explain_recommendation(rec_data, language)
        trace.append({
            "agent": "GraniteReasoningEngine",
            "status": "✓ success" if settings.is_granite_configured else "✓ success (template mode)",
            "latency_ms": 0,
            "label": "✓ Granite generated farmer-friendly explanation",
        })

        # ── Compile final response ─────────────────────────────
        sd = storage_result.data if storage_result.success else {}
        bd = buyer_result.data if buyer_result.success else {}

        return {
            "action": sd.get("action", "SELL_NOW"),
            "recommended_days": sd.get("recommended_days"),
            "current_price": current_price,
            "current_revenue": sd.get("current_revenue", current_price * quantity),
            "forecast_price": forecast_price,
            "forecast_confidence": forecast_confidence,
            "forecast_lower": forecast_result.data.get("lower_bound", forecast_price * 0.95) if forecast_result.success else forecast_price * 0.95,
            "forecast_upper": forecast_result.data.get("upper_bound", forecast_price * 1.05) if forecast_result.success else forecast_price * 1.05,
            "expected_future_revenue": sd.get("expected_future_gross", 0),
            "storage_cost": sd.get("storage_cost", 0),
            "transport_cost": sd.get("transport_cost", transport_cost_total),
            "quality_loss_cost": sd.get("quality_loss_cost", 0),
            "expected_net_revenue": sd.get("expected_net_revenue", 0),
            "potential_gain": sd.get("potential_gain", 0),
            "confidence": sd.get("confidence", 0.70),
            "reasoning": sd.get("reasoning", ""),
            "granite_explanation": granite_explanation,
            "best_buyer": bd.get("best_buyer"),
            "buyer_matches": bd.get("matches", [])[:3],
            "agent_trace": trace,
            "mandi_data": mandi_result.data,
            "forecast_series": forecast_result.data.get("forecast_series", []) if forecast_result.success else [],
            "income_data": income_result.data if income_result.success else {},
            "crop_name": crop_name,
            "is_demo": True,
            "disclaimer": "Forecasts are estimates. Actual market prices may differ. This is AI-assisted analysis, not financial advice.",
        }

    # ─────────────────── Chat Pipeline ────────────────────────

    async def handle_chat(
        self,
        message: str,
        language: str = "en",
        session_id: str = "",
        crop_id: Optional[str] = "crop_cotton",
        quantity: Optional[float] = None,
        district: Optional[str] = "Ahmedabad",
        history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        intent = detect_intent(message)
        trace: List[Dict[str, Any]] = [{"agent": "IntentDetector", "status": "✓ success", "label": f"✓ Intent detected: {intent}"}]

        # Get quick market context for Granite
        market_ctx: Dict[str, Any] = {}
        if crop_id:
            mandi_res = await self.mandi_agent._timed_run(crop_id=crop_id, district=district)
            trace.append({**mandi_res.to_trace(), "label": "✓ Market Agent fetched price context"})
            if mandi_res.success:
                market_ctx = {
                    "crop_name": mandi_res.data.get("crop_name", crop_id),
                    "current_price": mandi_res.data.get("current_price", 0),
                    "trend": mandi_res.data.get("trend", "stable"),
                    "market_name": mandi_res.data.get("primary_market_name", ""),
                }

        reply = await self.granite.chat(message, market_ctx, language, history or [])
        trace.append({"agent": "GraniteReasoningEngine", "status": "✓ success", "label": "✓ Granite generated response"})

        return {
            "reply": reply,
            "language": language,
            "intent": intent,
            "agent_trace": trace,
            "structured_data": market_ctx,
            "session_id": session_id,
            "is_demo": True,
        }

    # ─────────────────── Buyer Matching ───────────────────────

    async def match_buyers(self, crop_id: str, quantity: float,
                           quality_grade: str, district: str,
                           preferred_price: Optional[float] = None) -> Dict[str, Any]:
        result = await self.buyer_agent._timed_run(
            crop_id=crop_id, quantity=quantity, quality_grade=quality_grade,
            district=district, preferred_price=preferred_price
        )
        return result.data if result.success else {"matches": [], "error": result.error}

    # ─────────────────── Quality Assessment ───────────────────

    async def assess_quality(self, crop_type: str, image_url: Optional[str] = None,
                              image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        result = await self.quality_agent._timed_run(
            crop_type=crop_type, image_url=image_url, image_bytes=image_bytes
        )
        return result.data if result.success else {"error": result.error}

    # ─────────────────── Fallback ─────────────────────────────

    def _fallback_response(self, reason: str, trace: List) -> Dict[str, Any]:
        return {
            "action": "SELL_NOW",
            "recommended_days": None,
            "current_price": 0,
            "current_revenue": 0,
            "forecast_price": 0,
            "expected_net_revenue": 0,
            "potential_gain": 0,
            "confidence": 0.0,
            "reasoning": f"Unable to complete analysis: {reason}. Please sell at current market price.",
            "granite_explanation": f"Analysis unavailable: {reason}",
            "best_buyer": None,
            "buyer_matches": [],
            "agent_trace": trace,
            "is_demo": True,
            "error": reason,
        }


# ─────────────────────── Singleton ────────────────────────────

_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
