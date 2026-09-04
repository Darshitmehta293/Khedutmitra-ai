"""
AI API — Chat, Recommendation, Quality Assessment, Buyer Matching
"""
import uuid
import json
from decimal import Decimal
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.api.deps import get_current_user, require_farmer
from app.models.models import User, Recommendation
from app.agents.orchestrator import get_orchestrator
from app.schemas.schemas import ChatRequest, RecommendationRequest
from app.core.config import settings
from app.core.logging import logger


def _safe(obj: Any) -> Any:
    """Recursively convert Decimal/non-JSON-serializable types."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_safe(i) for i in obj]
    return obj

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    orch = get_orchestrator()
    session_id = payload.session_id or str(uuid.uuid4())
    result = await orch.handle_chat(
        message=payload.message,
        language=payload.language.value,
        session_id=session_id,
        crop_id=payload.crop_id,
        quantity=payload.quantity,
        district=payload.district or "Ahmedabad",
    )
    return result


@router.post("/recommendation")
async def get_recommendation(
    payload: RecommendationRequest,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    orch = get_orchestrator()
    ur = await db.execute(
        select(User).options(selectinload(User.farmer_profile)).where(User.id == current_user.id)
    )
    user_full = ur.scalar_one_or_none() or current_user
    farmer_profile = user_full.farmer_profile
    district = payload.district or (farmer_profile.district if farmer_profile else "Ahmedabad")

    result = await orch.get_full_recommendation(
        crop_id=payload.crop_id,
        quantity=payload.quantity,
        quality_grade=payload.quality_grade.value,
        district=district,
        storage_available=payload.storage_available,
        storage_cost_per_quintal_per_day=payload.storage_cost_per_quintal_per_day,
        transport_cost_total=payload.transport_cost_total,
        horizon_days=payload.horizon_days,
        farmer_name=current_user.name,
        language=current_user.language.value,
        inventory_id=payload.inventory_id,
    )
    stored = Recommendation(
        farmer_id=current_user.id,
        inventory_id=payload.inventory_id,
        action=result.get("action", "SELL_NOW"),
        recommended_days=result.get("recommended_days"),
        current_revenue=result.get("current_revenue"),
        expected_future_revenue=result.get("expected_future_revenue"),
        storage_cost=result.get("storage_cost"),
        transport_cost=result.get("transport_cost"),
        quality_loss_cost=result.get("quality_loss_cost"),
        expected_net_revenue=result.get("expected_net_revenue"),
        potential_gain=result.get("potential_gain"),
        confidence=result.get("confidence"),
        explanation=result.get("reasoning"),
        explanation_gu=result.get("granite_explanation") if current_user.language.value == "gu" else None,
        explanation_hi=result.get("granite_explanation") if current_user.language.value == "hi" else None,
        agent_trace=json.dumps(result.get("agent_trace", []), default=str),
    )
    db.add(stored)
    await db.commit()
    response = _safe(result)
    response["recommendation_id"] = stored.id
    return response


@router.get("/recommendations")
async def recommendation_history(
    limit: int = 20,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    limit = max(1, min(limit, 100))
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.farmer_id == current_user.id)
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return {
        "recommendations": [
            {
                "id": row.id,
                "inventory_id": row.inventory_id,
                "action": row.action.value,
                "recommended_days": row.recommended_days,
                "current_revenue": float(row.current_revenue or 0),
                "expected_net_revenue": float(row.expected_net_revenue or 0),
                "potential_gain": float(row.potential_gain or 0),
                "confidence": row.confidence,
                "explanation": row.explanation,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ],
        "total": len(rows),
    }


@router.post("/match-buyers")
async def match_buyers(
    crop_id: str,
    quantity: float,
    quality_grade: str = "B",
    district: str = "Ahmedabad",
    preferred_price: Optional[float] = None,
    current_user: User = Depends(get_current_user),
):
    orch = get_orchestrator()
    return await orch.match_buyers(crop_id, quantity, quality_grade, district, preferred_price)


@router.post("/forecast")
async def get_forecast(
    crop_id: str,
    market_id: str = "mkt_ahmedabad",
    horizon_days: int = 7,
    current_user: User = Depends(get_current_user),
):
    orch = get_orchestrator()
    result = await orch.forecast_agent._timed_run(crop_id=crop_id, market_id=market_id, horizon_days=horizon_days)
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@router.post("/quality-assessment")
async def quality_assessment(
    crop_type: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_farmer),
):
    image_bytes = None
    if image:
        if image.content_type not in settings.allowed_image_types_list:
            raise HTTPException(status_code=400, detail=f"Unsupported image type: {image.content_type}")
        content = await image.read()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(status_code=400, detail=f"Image too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")
        image_bytes = content

    orch = get_orchestrator()
    result = await orch.assess_quality(crop_type=crop_type, image_bytes=image_bytes)
    return result


@router.get("/demo-scenario")
async def demo_scenario(
    crop_id: str = "crop_cotton",
    quantity: float = 50.0,
    district: str = "Ahmedabad",
):
    """
    One-click demo scenario: Ramesh Patel, 50 quintals cotton, Ahmedabad.
    Runs full multi-agent pipeline and returns complete recommendation.
    """
    orch = get_orchestrator()
    result = await orch.get_full_recommendation(
        crop_id=crop_id,
        quantity=quantity,
        quality_grade="A",
        district=district,
        storage_available=True,
        storage_cost_per_quintal_per_day=0.5,
        transport_cost_total=2000.0,
        horizon_days=7,
        farmer_name="Ramesh Patel",
        language="en",
    )
    result["demo_farmer"] = "Ramesh Patel"
    result["demo_note"] = "DEMO SCENARIO - All data is simulated for demonstration purposes"
    return _safe(result)
