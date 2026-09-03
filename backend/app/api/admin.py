"""
Admin API — System health, user management, platform analytics
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.session import get_db
from app.models.models import User, FarmerInventory, BuyerListing
from app.api.deps import require_admin
from app.agents.orchestrator import get_orchestrator
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/system-health")
async def system_health(current_user: User = Depends(require_admin)):
    orch = get_orchestrator()
    provider_health = await orch.market_provider.health_check()
    return {
        "status": "ok",
        "database": "ok",
        "ai_service": "ok" if settings.is_granite_configured else "template_mode",
        "market_data_provider": provider_health["provider"],
        "granite_configured": settings.is_granite_configured,
        "demo_mode": settings.DEMO_MODE,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    total_users = await db.execute(select(func.count(User.id)))
    farmer_count = await db.execute(select(func.count(User.id)).where(User.role == "farmer"))
    buyer_count = await db.execute(select(func.count(User.id)).where(User.role == "buyer"))
    inv_count = await db.execute(select(func.count(FarmerInventory.id)).where(FarmerInventory.is_active == True))

    return {
        "total_users": total_users.scalar(),
        "farmers": farmer_count.scalar(),
        "buyers": buyer_count.scalar(),
        "active_inventory_items": inv_count.scalar(),
        "is_demo": settings.DEMO_MODE,
    }


@router.get("/users")
async def list_users(
    role: str = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    q = select(User)
    if role:
        q = q.where(User.role == role)
    result = await db.execute(q.limit(100))
    users = result.scalars().all()
    return {"users": [{"id": u.id, "name": u.name, "role": u.role, "created_at": u.created_at} for u in users]}
