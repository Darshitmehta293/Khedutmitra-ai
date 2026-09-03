"""
Auth API — Register, Login, Me
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.models import User, FarmerProfile, BuyerProfile, UserRole
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user
from app.core.logging import logger
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


async def _ensure_demo_user(payload: LoginRequest, db: AsyncSession) -> User | None:
    """Create the documented demo account when a deployment has no seeded database."""
    if not settings.DEMO_MODE or payload.phone != "9876543210" or payload.password != "demo1234":
        return None

    user = User(
        name="Ramesh Patel",
        phone="9876543210",
        email="9876543210@demo.khedutmitra.ai",
        password_hash=hash_password("demo1234"),
        role=UserRole.FARMER,
        language=Language.GUJARATI,
        location="Ahmedabad",
    )
    db.add(user)
    await db.flush()
    db.add(FarmerProfile(user_id=user.id, district="Ahmedabad", village="Bavla"))
    await db.commit()
    await db.refresh(user)
    logger.info("Demo user provisioned", user_id=user.id)
    return user


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check phone uniqueness
    existing = await db.execute(select(User).where(User.phone == payload.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    user = User(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        language=payload.language,
        location=payload.location,
    )
    db.add(user)
    await db.flush()

    # Create role-specific profile
    if payload.role == UserRole.FARMER:
        db.add(FarmerProfile(
            user_id=user.id,
            village=payload.village,
            district=payload.district,
        ))
    elif payload.role == UserRole.BUYER:
        if not payload.business_name or not payload.buyer_type:
            raise HTTPException(status_code=400, detail="Business name and buyer type required for buyer registration")
        profile = BuyerProfile(
            user_id=user.id,
            business_name=payload.business_name,
            buyer_type=payload.buyer_type,
        )
        db.add(profile)

    await db.commit()
    logger.info("User registered", user_id=user.id, role=payload.role)

    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(access_token=token, role=user.role, user_id=user.id, name=user.name)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()
    if not user:
        user = await _ensure_demo_user(payload, db)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    token = create_access_token(subject=user.id, role=user.role.value)
    logger.info("User logged in", user_id=user.id)
    return TokenResponse(access_token=token, role=user.role, user_id=user.id, name=user.name)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
