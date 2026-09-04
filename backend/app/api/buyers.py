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
    User, BuyerProfile, BuyerListing, Offer, Crop, FarmerInventory,
    UserRole, Language, CropCategory, BuyerType,
    OfferStatus,
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
    """Return active database listings plus demo listings for discovery."""
    result = await db.execute(
        select(BuyerListing).options(selectinload(BuyerListing.buyer_profile), selectinload(BuyerListing.crop))
        .where(BuyerListing.is_active == True)
    )
    listings = []
    for listing in result.scalars().all():
        if crop_id and listing.crop_id != crop_id:
            continue
        if district and listing.district and listing.district.lower() != district.lower():
            continue
        listings.append({
            "id": listing.id, "business_name": listing.buyer_profile.business_name,
            "buyer_type": listing.buyer_profile.buyer_type.value, "crop_id": listing.crop_id,
            "min_quantity": listing.min_quantity, "max_quantity": listing.max_quantity,
            "quality_requirement": listing.quality_requirement.value, "offered_price": float(listing.offered_price),
            "district": listing.district, "delivery_days": listing.delivery_days,
            "is_demo": listing.is_demo,
        })
    demo = [b for b in DEMO_BUYERS if not crop_id or b["crop_id"] == crop_id]
    return {"buyers": listings + demo, "total": len(listings) + len(demo), "is_demo": not listings}


@router.get("/matches")
async def get_buyer_matches(
    crop_id: str = Query("crop_cotton"),
    quantity: float = Query(50.0),
    quality_grade: str = Query("B"),
    district: str = Query("Ahmedabad"),
    preferred_price: Optional[float] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    orch = get_orchestrator()
    listing_result = await db.execute(
        select(BuyerListing).options(selectinload(BuyerListing.buyer_profile))
        .where(BuyerListing.is_active == True, BuyerListing.crop_id == crop_id)
    )
    database_buyers = []
    for listing in listing_result.scalars().all():
        profile = listing.buyer_profile
        database_buyers.append({
            "id": listing.id, "business_name": profile.business_name,
            "buyer_type": profile.buyer_type.value, "crop_id": listing.crop_id,
            "min_quantity": listing.min_quantity, "max_quantity": listing.max_quantity,
            "quality_requirement": listing.quality_requirement.value,
            "offered_price": float(listing.offered_price), "district": listing.district or profile.district,
            "delivery_days": listing.delivery_days, "lat": listing.latitude or profile.latitude or 22.3,
            "lon": listing.longitude or profile.longitude or 71.0,
            "is_demo": listing.is_demo, "contact_phone": None,
        })
    buyers = database_buyers or DEMO_BUYERS
    result = await orch.match_buyers(crop_id, quantity, quality_grade, district, preferred_price, buyers)
    return result


@router.post("/offers", response_model=OfferOut, status_code=201)
async def create_offer(
    payload: OfferCreate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db),
):
    listing = await _get_or_create_demo_listing(payload.buyer_listing_id, db)
    if payload.quantity < listing.min_quantity or payload.quantity > listing.max_quantity:
        raise HTTPException(status_code=400, detail="Quantity must fit the buyer listing range")
    if payload.inventory_id:
        inventory_result = await db.execute(
            select(FarmerInventory).where(
                FarmerInventory.id == payload.inventory_id,
                FarmerInventory.farmer_id == current_user.id,
                FarmerInventory.is_active == True,
            )
        )
        inventory = inventory_result.scalar_one_or_none()
        if not inventory or inventory.quantity < payload.quantity:
            raise HTTPException(status_code=400, detail="Offer quantity exceeds available inventory")
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
    try:
        requested_status = OfferStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid offer status")
    is_farmer = str(offer.farmer_id) == str(current_user.id)
    buyer_profile = await db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == current_user.id))
    is_buyer = bool(buyer_profile and str(offer.buyer_listing.buyer_profile_id) == str(buyer_profile.id))
    if not (is_farmer or is_buyer):
        raise HTTPException(status_code=403, detail="Not authorized")
    if offer.status != OfferStatus.PENDING:
        raise HTTPException(status_code=409, detail="Only pending offers can change status")
    if is_farmer and requested_status not in {OfferStatus.WITHDRAWN, OfferStatus.REJECTED}:
        raise HTTPException(status_code=403, detail="Farmers can withdraw or reject pending offers")
    if is_buyer and requested_status not in {OfferStatus.ACCEPTED, OfferStatus.REJECTED}:
        raise HTTPException(status_code=403, detail="Buyers can accept or reject pending offers")
    offer.status = requested_status
    await db.commit()
    return {"id": offer_id, "status": requested_status.value}


@router.get("/offers", response_model=List[OfferOut])
async def list_offers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Offer).options(selectinload(Offer.buyer_listing))
    if current_user.role == UserRole.FARMER:
        query = query.where(Offer.farmer_id == current_user.id)
    elif current_user.role == UserRole.BUYER:
        profile = await db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == current_user.id))
        if not profile:
            return []
        query = query.where(Offer.buyer_listing.has(buyer_profile_id=profile.id))
    else:
        raise HTTPException(status_code=403, detail="Role cannot view offers")
    result = await db.execute(query.order_by(Offer.created_at.desc()))
    return result.scalars().all()


@router.post("/listings", status_code=201)
async def create_listing(
    payload: BuyerListingCreate,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db),
):
    if payload.max_quantity < payload.min_quantity:
        raise HTTPException(status_code=400, detail="Maximum quantity must be at least minimum quantity")
    profile = await db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == current_user.id))
    if not profile:
        raise HTTPException(status_code=400, detail="Create a buyer profile before publishing a listing")
    if not await db.get(Crop, payload.crop_id):
        raise HTTPException(status_code=404, detail="Crop not found")
    listing = BuyerListing(
        buyer_profile_id=profile.id, crop_id=payload.crop_id,
        min_quantity=payload.min_quantity, max_quantity=payload.max_quantity,
        quality_requirement=payload.quality_requirement, offered_price=payload.offered_price,
        district=payload.district, delivery_days=payload.delivery_days, is_demo=False,
    )
    db.add(listing)
    await db.commit()
    return {"id": listing.id, "message": "Listing published"}


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
