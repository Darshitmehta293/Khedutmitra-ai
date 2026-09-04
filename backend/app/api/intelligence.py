"""Farmer intelligence extensions: weather, demand, logistics, finance and trust."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.orchestrator import get_orchestrator
from app.api.deps import get_current_user, require_farmer, require_admin
from app.database.session import get_db
from app.models.models import (
    User, FarmerProfile, FarmerInventory, PriceAlert, Expense, Deal, Offer,
    Rating, Cooperative, CooperativeMember, UserRole,
)

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

DISTRICT_WEATHER = {
    "Ahmedabad": {"temperature_c": 31, "humidity_percent": 58, "rainfall_mm": 1.2},
    "Rajkot": {"temperature_c": 30, "humidity_percent": 54, "rainfall_mm": 0.8},
    "Junagadh": {"temperature_c": 29, "humidity_percent": 64, "rainfall_mm": 2.4},
}


def _weather(district: str):
    base = DISTRICT_WEATHER.get(district, {"temperature_c": 30, "humidity_percent": 60, "rainfall_mm": 1.0})
    days = []
    for offset in range(5):
        rainfall = round(max(0, base["rainfall_mm"] + (offset % 3 - 1) * 1.8), 1)
        days.append({
            "date": (datetime.utcnow() + timedelta(days=offset)).date().isoformat(),
            **base, "rainfall_mm": rainfall,
            "alert": "Drying conditions are favorable" if rainfall < 3 else "Protect harvested crop from moisture",
        })
    return days


@router.get("/weather")
async def weather(district: str = "Ahmedabad", current_user: User = Depends(get_current_user)):
    return {"district": district, "forecast": _weather(district), "source": "demo_weather", "is_demo": True}


@router.get("/demand")
async def demand(crop_id: str = "crop_cotton", current_user: User = Depends(get_current_user)):
    orch = get_orchestrator()
    prices = await orch.market_provider.get_current_prices(crop_id)
    current = sum(float(p.modal_price) for p in prices) / max(1, len(prices))
    demand_index = 68 if crop_id == "crop_cotton" else 73
    return {"crop_id": crop_id, "current_demand_index": demand_index, "outlook": "rising", "peak_window_days": 14,
            "expected_price_signal": round(current * 1.025, 2), "confidence": 0.62, "is_demo": True}


@router.get("/mandi-comparison")
async def mandi_comparison(crop_id: str = "crop_cotton", quantity: float = Query(50, gt=0), district: str = "Ahmedabad", current_user: User = Depends(get_current_user)):
    orch = get_orchestrator()
    prices = await orch.market_provider.get_current_prices(crop_id)
    rows = []
    for price in prices:
        distance = 0 if price.market_id.endswith("ahmedabad") else 45
        transport = round(700 + distance * 18 + quantity * 2, 2)
        rows.append({"market_id": price.market_id, "market_name": price.market_name, "modal_price": float(price.modal_price),
                     "gross_revenue": round(float(price.modal_price) * quantity, 2), "transport_cost": transport,
                     "net_revenue": round(float(price.modal_price) * quantity - transport, 2), "distance_km": distance})
    return {"crop_id": crop_id, "quantity": quantity, "markets": sorted(rows, key=lambda row: row["net_revenue"], reverse=True), "is_demo": True}


@router.get("/logistics")
async def logistics(distance_km: float = Query(50, ge=0), quantity: float = Query(50, gt=0), current_user: User = Depends(get_current_user)):
    base = 700 + distance_km * 18
    return {"distance_km": distance_km, "quantity": quantity, "estimated_cost": round(base + quantity * 2, 2),
            "cost_per_quintal": round((base + quantity * 2) / quantity, 2), "vehicle_type": "10-ton truck", "is_demo": True}


@router.get("/storage")
async def storage(district: str = "Ahmedabad", current_user: User = Depends(get_current_user)):
    return {"district": district, "facilities": [
        {"id": "warehouse-1", "name": "Gujarat Agro Warehouse", "distance_km": 12, "cost_per_quintal_day": 0.65, "capacity_quintals": 5000, "available": True},
        {"id": "warehouse-2", "name": "Farmer Cooperative Storage", "distance_km": 24, "cost_per_quintal_day": 0.48, "capacity_quintals": 1800, "available": True},
    ], "is_demo": True}


@router.post("/negotiation")
async def negotiation(payload: dict = Body(...), current_user: User = Depends(get_current_user)):
    price = float(payload.get("offered_price", payload.get("current_price", 0)))
    return {"asking_price": round(price * 1.05, 2), "walk_away_price": round(price * 0.98, 2),
            "negotiation_range": [round(price * 0.98, 2), round(price * 1.05, 2)],
            "talking_points": ["Mention your quality grade", "Compare nearby mandi net prices", "Confirm delivery and payment terms"], "is_demo": True}


@router.post("/alerts")
async def create_alert(payload: dict = Body(...), current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    direction = payload.get("direction", "above")
    if direction not in {"above", "below"}:
        raise HTTPException(400, "Direction must be above or below")
    alert = PriceAlert(farmer_id=current_user.id, crop_id=payload["crop_id"], threshold_price=float(payload["threshold_price"]), direction=direction)
    db.add(alert); await db.commit(); await db.refresh(alert)
    return {"id": alert.id, "crop_id": alert.crop_id, "threshold_price": alert.threshold_price, "direction": alert.direction, "is_active": alert.is_active}


@router.get("/alerts")
async def alerts(current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PriceAlert).where(PriceAlert.farmer_id == current_user.id).order_by(PriceAlert.created_at.desc()))
    return {"alerts": [{"id": a.id, "crop_id": a.crop_id, "threshold_price": a.threshold_price, "direction": a.direction, "is_active": a.is_active} for a in result.scalars()]}


@router.get("/notifications")
async def notifications(current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PriceAlert).where(PriceAlert.farmer_id == current_user.id, PriceAlert.is_active == True))
    return {"notifications": [{"type": "price_alert", "message": f"Alert active for {a.crop_id} at Rs {a.threshold_price:,.0f}", "created_at": a.created_at.isoformat()} for a in result.scalars()], "delivery": "in_app", "is_demo": True}


@router.get("/profile")
async def get_profile(current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    profile = await db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
    return {"name": current_user.name, "phone": current_user.phone, "location": current_user.location, "village": profile.village if profile else None, "district": profile.district if profile else None, "farm_size_acres": profile.farm_size_acres if profile else None}


@router.put("/profile")
async def update_profile(payload: dict = Body(...), current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    current_user.name = payload.get("name", current_user.name); current_user.location = payload.get("location", current_user.location)
    profile = await db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
    if not profile:
        profile = FarmerProfile(user_id=current_user.id); db.add(profile)
    for field in ("village", "district", "state", "farm_size_acres"):
        if field in payload: setattr(profile, field, payload[field])
    await db.commit()
    return await get_profile(current_user, db)


@router.post("/expenses")
async def create_expense(payload: dict = Body(...), current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    amount = float(payload.get("amount", 0))
    if amount <= 0: raise HTTPException(400, "Amount must be greater than zero")
    expense = Expense(farmer_id=current_user.id, crop_id=payload.get("crop_id"), category=payload["category"], amount=amount, notes=payload.get("notes"))
    db.add(expense); await db.commit(); await db.refresh(expense)
    return {"id": expense.id, "category": expense.category, "amount": amount, "created_at": expense.created_at.isoformat()}


@router.get("/profit")
async def profit(current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    inventory = await db.scalar(select(func.coalesce(func.sum(FarmerInventory.quantity), 0)).where(FarmerInventory.farmer_id == current_user.id, FarmerInventory.is_active == True))
    expenses = await db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.farmer_id == current_user.id))
    estimated_revenue = float(inventory or 0) * 7000
    return {"inventory_quintals": float(inventory or 0), "estimated_revenue": estimated_revenue, "expenses": float(expenses or 0), "estimated_profit": estimated_revenue - float(expenses or 0), "is_demo": True}


@router.get("/risk")
async def risk(crop_id: str = "crop_cotton", district: str = "Ahmedabad", current_user: User = Depends(get_current_user)):
    return {"crop_id": crop_id, "risks": [{"name": "Price volatility", "level": "medium", "mitigation": "Set a price alert and compare net mandi prices"}, {"name": "Moisture exposure", "level": "low", "mitigation": "Use covered storage and monitor rainfall"}, {"name": "Demand uncertainty", "level": "medium", "mitigation": "Collect buyer quotes before committing"}], "is_demo": True}


@router.get("/schemes")
async def schemes(current_user: User = Depends(get_current_user)):
    return {"schemes": [{"name": "PM-KISAN", "summary": "Income support for eligible farmer families", "source": "myScheme.gov.in"}, {"name": "Kisan Credit Card", "summary": "Working capital support for cultivation", "source": "Government of India"}], "disclaimer": "Check eligibility and current deadlines with an official source.", "is_demo": True}


@router.get("/news")
async def news(current_user: User = Depends(get_current_user)):
    return {"items": [{"headline": "Cotton demand remains firm across Gujarat mills", "summary": "Local demand indicators are moderately positive; verify prices before selling.", "published_at": datetime.utcnow().date().isoformat()}], "source": "demo_market_digest", "is_demo": True}


@router.post("/ratings")
async def rate(payload: dict = Body(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    score = int(payload.get("score", 0))
    if score < 1 or score > 5: raise HTTPException(400, "Score must be between 1 and 5")
    rating = Rating(rater_id=current_user.id, rated_user_id=payload["rated_user_id"], offer_id=payload.get("offer_id"), score=score, comment=payload.get("comment"))
    db.add(rating); await db.commit(); return {"id": rating.id, "score": score}


@router.post("/cooperative")
async def create_cooperative(payload: dict = Body(...), current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    name = str(payload.get("name", "")).strip()
    if len(name) < 3:
        raise HTTPException(400, "Cooperative name is required")
    cooperative = Cooperative(name=name, district=payload.get("district"), created_by=current_user.id)
    db.add(cooperative); await db.flush()
    db.add(CooperativeMember(cooperative_id=cooperative.id, farmer_id=current_user.id))
    await db.commit()
    return {"id": cooperative.id, "name": cooperative.name, "message": "Cooperative created"}


@router.get("/cooperative")
async def cooperative(current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    membership = await db.scalar(select(CooperativeMember).where(CooperativeMember.farmer_id == current_user.id))
    if not membership: return {"member": False, "cooperatives": []}
    coop = await db.get(Cooperative, membership.cooperative_id)
    quantity = await db.scalar(select(func.coalesce(func.sum(FarmerInventory.quantity), 0)).join(CooperativeMember, CooperativeMember.farmer_id == FarmerInventory.farmer_id).where(CooperativeMember.cooperative_id == coop.id, FarmerInventory.is_active == True))
    return {"member": True, "cooperative": {"id": coop.id, "name": coop.name, "members_quantity": float(quantity or 0)}, "bulk_ready": float(quantity or 0) >= 100}


@router.get("/explain/{recommendation_id}")
async def explain(recommendation_id: str, current_user: User = Depends(require_farmer), db: AsyncSession = Depends(get_db)):
    from app.models.models import Recommendation
    recommendation = await db.scalar(select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.farmer_id == current_user.id))
    if not recommendation: raise HTTPException(404, "Recommendation not found")
    return {"recommendation_id": recommendation.id, "decision": recommendation.action.value, "factors": {"market": "Current mandi modal price", "forecast": "Baseline forecast confidence", "costs": "Storage, transport, and quality-loss economics", "buyer": "Available compatible buyer listings"}, "trace": recommendation.agent_trace, "explanation": recommendation.explanation}


@router.get("/admin-analytics")
async def admin_analytics(current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    users = await db.scalar(select(func.count(User.id))); offers = await db.scalar(select(func.count(Offer.id))); expenses = await db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)))
    return {"users": users, "offers": offers, "tracked_expenses": float(expenses or 0), "agent_performance": {"market": "available", "forecast": "available", "matching": "available"}, "is_demo": True}
