# -*- coding: utf-8 -*-
"""
KhedutMitra AI - Database Seed Script
Populates demo data: crops, mandis, market prices, sample users.
Run: python -m app.database.seed
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import AsyncSessionLocal, create_tables
from app.models.models import (
    User, FarmerProfile, BuyerProfile, Crop, MandiMarket,
    MarketPrice, FarmerInventory,
    UserRole, Language, CropCategory, QualityGrade, BuyerType
)
from app.core.security import hash_password
from app.services.market_data_provider import DEMO_MARKETS, DEMO_BASE_PRICES
import random

print("KhedutMitra AI -- Seeding demo data...")


async def seed():
    await create_tables()
    async with AsyncSessionLocal() as db:
        await seed_crops(db)
        await seed_markets(db)
        await seed_prices(db)
        await seed_demo_users(db)
        await db.commit()
    print("  OK Demo data seeded successfully!")


async def seed_crops(db: AsyncSession):
    crops_data = [
        Crop(id="crop_cotton", name="Cotton", name_gu="kapas", name_hi="kapas",
             category=CropCategory.COTTON, unit="quintal"),
        Crop(id="crop_groundnut", name="Groundnut", name_gu="mungfali", name_hi="mungfali",
             category=CropCategory.GROUNDNUT, unit="quintal"),
    ]
    for c in crops_data:
        existing = await db.get(Crop, c.id)
        if not existing:
            db.add(c)
    print("  OK Crops seeded")


async def seed_markets(db: AsyncSession):
    for m in DEMO_MARKETS:
        existing = await db.get(MandiMarket, m["id"])
        if not existing:
            db.add(MandiMarket(
                id=m["id"],
                name=m["name"],
                name_gu=m.get("name_gu"),
                district=m["district"],
                state=m["state"],
                latitude=m["lat"],
                longitude=m["lon"],
            ))
    print("  OK Markets seeded")


async def seed_prices(db: AsyncSession):
    today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    crop_ids = ["crop_cotton", "crop_groundnut"]
    crop_keys = {"crop_cotton": "cotton", "crop_groundnut": "groundnut"}

    for m in DEMO_MARKETS:
        for cid in crop_ids:
            ck = crop_keys[cid]
            base = DEMO_BASE_PRICES.get(ck, {}).get(m["id"].replace("mkt_", ""), 6500)

            for day_offset in range(60, 0, -1):
                day = today - timedelta(days=day_offset)
                rng = random.Random(hash(m["id"] + cid) + day_offset * 37)
                pct = rng.uniform(-0.022, 0.028)
                trend = 1 + (60 - day_offset) * 0.0008
                modal = round(base * trend * (1 + pct), 2)

                existing = await db.execute(
                    select(MarketPrice).where(
                        MarketPrice.market_id == m["id"],
                        MarketPrice.crop_id == cid,
                        MarketPrice.price_date == day,
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                db.add(MarketPrice(
                    market_id=m["id"],
                    crop_id=cid,
                    price_date=day,
                    min_price=round(modal * 0.965, 2),
                    max_price=round(modal * 1.023, 2),
                    modal_price=modal,
                    arrivals_tonnes=round(rng.uniform(80, 600), 1),
                    source="demo_data",
                    is_demo=True,
                ))
    print("  OK Market prices seeded (60 days x 8 markets x 2 crops)")


async def seed_demo_users(db: AsyncSession):
    demo_farmers = [
        {
            "name": "Ramesh Patel", "phone": "9876543210",
            "district": "Ahmedabad", "village": "Bavla",
            "crop_id": "crop_cotton", "qty": 50, "grade": QualityGrade.A,
        },
        {
            "name": "Savitaben Desai", "phone": "9876543211",
            "district": "Rajkot", "village": "Jasdan",
            "crop_id": "crop_groundnut", "qty": 75, "grade": QualityGrade.B,
        },
        {
            "name": "Haribhai Solanki", "phone": "9876543212",
            "district": "Junagadh", "village": "Veraval",
            "crop_id": "crop_cotton", "qty": 30, "grade": QualityGrade.B,
        },
    ]

    for f in demo_farmers:
        result = await db.execute(select(User).where(User.phone == f["phone"]))
        if result.scalar_one_or_none():
            continue

        user = User(
            name=f["name"], phone=f["phone"],
            email=f"{f['phone']}@demo.khedutmitra.ai",
            password_hash=hash_password("demo1234"),
            role=UserRole.FARMER,
            language=Language.GUJARATI,
            location=f["district"],
        )
        db.add(user)
        await db.flush()

        db.add(FarmerProfile(user_id=user.id, district=f["district"], village=f["village"]))
        db.add(FarmerInventory(
            farmer_id=user.id, crop_id=f["crop_id"],
            quantity=f["qty"], quality_grade=f["grade"],
            storage_available=True,
            storage_cost_per_quintal_per_day=0.5,
            district=f["district"],
        ))

    # Demo admin
    admin_result = await db.execute(select(User).where(User.phone == "9000000000"))
    if not admin_result.scalar_one_or_none():
        db.add(User(
            name="Admin", phone="9000000000",
            email="admin@khedutmitra.ai",
            password_hash=hash_password("admin1234"),
            role=UserRole.ADMIN,
            language=Language.ENGLISH,
        ))

    print("  OK Demo users seeded")
    print("  [creds] Farmer - Phone: 9876543210  Password: demo1234  (Ramesh Patel)")
    print("  [creds] Admin  - Phone: 9000000000  Password: admin1234")


if __name__ == "__main__":
    asyncio.run(seed())
