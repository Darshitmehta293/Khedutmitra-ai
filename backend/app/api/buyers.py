"""
Buyers API — Listings, Offers, Marketplace
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.models.models import (
    User, BuyerProfile, BuyerListing, Offer, Crop,
    UserRole, Language, CropCategory, BuyerType,
)
from app.schemas.schemas import (
    BuyerListingCreate, BuyerProfileCreate, OfferCreate, OfferOut, BuyerMatchRequest
)
from app.api.deps import get_current_user, require_farmer, require_buyer
from app.agents.orchestrator import get_orchestrator
from app.core.logging import logger
from app.agents.buyer_matching_agent import DEMO_BUYERS

router = APIRouter(prefix="/buyers", tags=["buyers"])


async def _get_or_create_demo_listing(listing_id: str, db: AsyncSession) -> BuyerListing:
    listing = await db.get(BuyerListing, listing_id)
    if listing:
        return listing

    demo_buyer = next((buyer for buyer in DEMO_BUYERS if buyer["id"] == listing_id), None)
    if not demo_buyer:
        raise HTTPException(status_code=404, detail="Buyer listing not found")

    buyer_email = f"{listing_id}@demo.khedutmitra.ai"
    user_result = await db.execute(select(User).where(User.email == buyer_email))
    buyer_user = user_result.scalar_one_or_none()
    if not buyer_user:
        buyer_user = User(
            name=demo_buyer["business_name"],
            phone=f"900000{listing_id[-1]}",
            email=buyer_email,
            password_hash="demo-buyer-account",
            role=UserRole.BUYER,
            language=Language.ENGLISH,
            location=demo_buyer["district"],
        )
        db.add(buyer_user)
        await db.flush()

    profile_result = await db.execute(
        select(BuyerProfile).where(BuyerProfile.user_id == buyer_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        profile = BuyerProfile(
            user_id=buyer_user.id,
            business_name=demo_buyer["business_name"],
            buyer_type=BuyerType(demo_buyer["buyer_type"]),
            district=demo_buyer["district"],
        )
        db.add(profile)
        await db.flush()

    crop = await db.get(Crop, demo_buyer["crop_id"])
    if not crop:
        crop = Crop(
            id=demo_buyer["crop_id"],
            name=demo_buyer["crop_id"].replace("crop_", "").title(),
            category=CropCategory.COTTON if demo_buyer["crop_id"] == "crop_cotton" else CropCategory.GROUNDNUT,
            unit="quintal",
        )
        db.add(crop)
        await db.flush()

    listing = BuyerListing(
        id=listing_id,
        buyer_profile_id=profile.id,
        crop_id=crop.id,
        min_quantity=demo_buyer["min_quantity"],
        max_quantity=demo_buyer["max_quantity"],
        quality_requirement=demo_buyer["quality_requirement"],
        offered_price=demo_buyer["offered_price"],
        district=demo_buyer["district"],
        delivery_days=demo_buyer["delivery_days"],
        is_demo=True,
    )
    db.add(listing)
    await db.flush()
    return listing


@router.get("")
async def list_buyers(
    crop_id: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return demo buyer listings with match scores if crop/district provided."""
    orch = get_orchestrator()
    from app.agents.buyer_matching_agent import DEMO_BUYERS

    buyers = DEMO_BUYERS
    if crop_id:
        buyers = [b for b in buyers if b["crop_id"] == crop_id]

    return {"buyers": buyers, "total": len(buyers), "is_demo": True,
            "note": "DEMO DATA — buyer listings for demonstration"}


@router.get("/matches")
async def get_buyer_matches(
    crop_id: str = Query("crop_cotton"),
    quantity: float = Query(50.0),
    quality_grade: str = Query("B"),
    district: str = Query("Ahmedabad"),
    preferred_price: Optional[float] = Query(None),
    current_user: User = Depends(get_current_user),
):
    orch = get_orchestrator()
    result = await orch.match_buyers(crop_id, quantity, quality_grade, district, preferred_price)
    return result


@router.post("/offers", response_model=OfferOut, status_code=201)
async def create_offer(
    payload: OfferCreate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    await _get_or_create_demo_listing(payload.buyer_listing_id, db)
    offer = Offer(
        farmer_id=current_user.id,
        buyer_listing_id=payload.buyer_listing_id,
        inventory_id=payload.inventory_id,
        quantity=payload.quantity,
        offered_price=payload.offered_price,
        message=payload.message,
    )
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
    return offer


@router.put("/offers/{offer_id}")
async def update_offer_status(
    offer_id: str,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Offer).where(Offer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    # Farmer can only update their own offers
    if str(offer.farmer_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    offer.status = new_status
    await db.commit()
    return {"id": offer_id, "status": new_status}


@router.post("/profile")
async def create_buyer_profile(
    payload: BuyerProfileCreate,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db),
):
    profile = BuyerProfile(
        user_id=current_user.id,
        business_name=payload.business_name,
        buyer_type=payload.buyer_type,
        address=payload.address,
        district=payload.district,
        gst_number=payload.gst_number,
    )
    db.add(profile)
    await db.commit()
    return {"message": "Buyer profile created", "id": profile.id}
