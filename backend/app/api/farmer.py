"""
Farmer API — Dashboard, Inventory CRUD
"""
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.models.models import User, FarmerInventory, Crop
from app.schemas.schemas import InventoryCreate, InventoryUpdate, InventoryOut, DashboardOut
from app.api.deps import require_farmer
from app.agents.orchestrator import get_orchestrator
from app.core.logging import logger


def _safe(obj):
    """Recursively convert Decimal/non-JSON types to float/str."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_safe(i) for i in obj]
    return obj

router = APIRouter(prefix="/farmer", tags=["farmer"])


@router.get("/dashboard")
async def dashboard(
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    orch = get_orchestrator()

    # Eagerly load farmer_profile to avoid lazy-load outside session
    user_result = await db.execute(
        select(User)
        .options(selectinload(User.farmer_profile))
        .where(User.id == current_user.id)
    )
    user_full = user_result.scalar_one_or_none() or current_user

    # Load inventory
    result = await db.execute(
        select(FarmerInventory)
        .options(selectinload(FarmerInventory.crop))
        .where(FarmerInventory.farmer_id == current_user.id, FarmerInventory.is_active == True)
    )
    inventory_items = result.scalars().all()

    inv_list = [
        {"crop_id": i.crop.id if i.crop else "", "quantity": i.quantity, "district": i.district or "Ahmedabad"}
        for i in inventory_items
    ]

    # Determine primary crop and district
    crop_id = inv_list[0]["crop_id"] if inv_list else "crop_cotton"
    district = inv_list[0]["district"] if inv_list else "Ahmedabad"

    # Quick price + forecast for dashboard
    mandi_data = {}
    forecast_data = {}
    buyer_data = {"matches": []}
    try:
        market_prov = orch.market_provider
        prices = await market_prov.get_current_prices(crop_id)
        if prices:
            p = prices[0]
            mandi_data = {"current_price": float(p.modal_price), "crop_name": p.crop_name, "is_demo": True}

        fc = await orch.forecast_service.forecast_single(crop_id, "mkt_ahmedabad", 7)
        forecast_data = {"predicted_price": fc.predicted_price}

        buyer_data = await orch.match_buyers(crop_id, sum(i["quantity"] for i in inv_list) or 50, "B", district)
    except Exception as e:
        logger.warning("Dashboard agent partial failure", error=str(e))

    farmer_profile = user_full.farmer_profile
    district_name = farmer_profile.district if farmer_profile else district

    # Income agent summary
    income_res = await orch.income_agent._timed_run(
        farmer_name=current_user.name,
        district=district_name,
        inventory=inv_list,
        price_data=mandi_data,
        forecast_data=forecast_data,
        buyer_matches=buyer_data.get("matches", []),
    )
    income_data = income_res.data if income_res.success else {}

    return _safe({
        "farmer_name": current_user.name,
        "district": district_name,
        "total_inventory_quintals": income_data.get("total_inventory_quintals", 0),
        "cotton_quintals": income_data.get("cotton_quintals", 0),
        "groundnut_quintals": income_data.get("groundnut_quintals", 0),
        "current_estimated_value": income_data.get("current_estimated_value", 0),
        "expected_value_7d": income_data.get("expected_value_7d", 0),
        "potential_gain": income_data.get("potential_gain", 0),
        "active_buyer_opportunities": income_data.get("active_buyer_opportunities", 0),
        "current_price": mandi_data.get("current_price", 0),
        "forecast_price_7d": forecast_data.get("predicted_price", 0),
        "recommendation_action": income_data.get("recommendation_action", "SELL_NOW"),
        "revenue_scenarios": income_data.get("revenue_scenarios", []),
        "top_buyers": income_data.get("top_buyers", []),
        "is_demo": True,
    })


@router.get("/inventory", response_model=List[InventoryOut])
async def get_inventory(
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FarmerInventory)
        .options(selectinload(FarmerInventory.crop))
        .where(FarmerInventory.farmer_id == current_user.id, FarmerInventory.is_active == True)
    )
    return result.scalars().all()


@router.post("/inventory", response_model=InventoryOut, status_code=201)
async def create_inventory(
    payload: InventoryCreate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    # Validate crop exists
    crop = await db.get(Crop, payload.crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    item = FarmerInventory(
        farmer_id=current_user.id,
        crop_id=payload.crop_id,
        quantity=payload.quantity,
        quality_grade=payload.quality_grade,
        harvest_date=payload.harvest_date,
        storage_available=payload.storage_available,
        storage_cost_per_quintal_per_day=payload.storage_cost_per_quintal_per_day,
        village=payload.village,
        district=payload.district,
        notes=payload.notes,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    # Reload with relationship
    result = await db.execute(
        select(FarmerInventory).options(selectinload(FarmerInventory.crop)).where(FarmerInventory.id == item.id)
    )
    return result.scalar_one()


@router.put("/inventory/{item_id}", response_model=InventoryOut)
async def update_inventory(
    item_id: str,
    payload: InventoryUpdate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FarmerInventory).options(selectinload(FarmerInventory.crop))
        .where(FarmerInventory.id == item_id, FarmerInventory.farmer_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/inventory/{item_id}", status_code=204)
async def delete_inventory(
    item_id: str,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FarmerInventory)
        .where(FarmerInventory.id == item_id, FarmerInventory.farmer_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    item.is_active = False
    await db.commit()
