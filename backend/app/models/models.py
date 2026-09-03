"""
KhedutMitra AI — All SQLAlchemy ORM Models
Compatible with both SQLite (local dev) and PostgreSQL (production).
"""
import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint, Index, Numeric
)
from sqlalchemy.orm import relationship

from app.database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


# ─────────────────────── Enums ────────────────────────────────

class UserRole(str, enum.Enum):
    FARMER = "farmer"
    BUYER = "buyer"
    ADMIN = "admin"


class Language(str, enum.Enum):
    GUJARATI = "gu"
    HINDI = "hi"
    ENGLISH = "en"


class CropCategory(str, enum.Enum):
    COTTON = "cotton"
    GROUNDNUT = "groundnut"


class QualityGrade(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    UNGRADED = "ungraded"


class RecommendationAction(str, enum.Enum):
    SELL_NOW = "SELL_NOW"
    STORE = "STORE"
    WAIT = "WAIT"


class OfferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"


class BuyerType(str, enum.Enum):
    GINNING_MILL = "ginning_mill"
    OIL_MILL = "oil_mill"
    TRADER = "trader"
    EXPORTER = "exporter"
    PROCESSOR = "processor"


# ─────────────────────── User / Profile ────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(120), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(180), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.FARMER)
    language = Column(Enum(Language), nullable=False, default=Language.GUJARATI)
    location = Column(String(120), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer_profile = relationship("FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    buyer_profile = relationship("BuyerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    inventory = relationship("FarmerInventory", back_populates="farmer", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="farmer", cascade="all, delete-orphan")
    quality_assessments = relationship("QualityAssessment", back_populates="farmer", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="farmer", cascade="all, delete-orphan")


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    village = Column(String(120), nullable=True)
    district = Column(String(120), nullable=True)
    state = Column(String(80), nullable=False, default="Gujarat")
    preferred_language = Column(Enum(Language), default=Language.GUJARATI)
    farm_size_acres = Column(Float, nullable=True)
    aadhaar_number = Column(String(12), nullable=True)
    bank_account_number = Column(String(20), nullable=True)
    ifsc_code = Column(String(11), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="farmer_profile")


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    business_name = Column(String(200), nullable=False)
    buyer_type = Column(Enum(BuyerType), nullable=False)
    address = Column(Text, nullable=True)
    district = Column(String(120), nullable=True)
    state = Column(String(80), default="Gujarat")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    gst_number = Column(String(15), nullable=True)
    verification_status = Column(String(20), default="pending")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="buyer_profile")
    buyer_listings = relationship("BuyerListing", back_populates="buyer_profile", cascade="all, delete-orphan")


# ─────────────────────── Crops ────────────────────────────────

class Crop(Base):
    __tablename__ = "crops"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(80), nullable=False)
    name_gu = Column(String(80), nullable=True)
    name_hi = Column(String(80), nullable=True)
    category = Column(Enum(CropCategory), nullable=False)
    unit = Column(String(20), default="quintal")
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    inventory = relationship("FarmerInventory", back_populates="crop")
    market_prices = relationship("MarketPrice", back_populates="crop")
    forecasts = relationship("Forecast", back_populates="crop")
    buyer_listings = relationship("BuyerListing", back_populates="crop")


class FarmerInventory(Base):
    __tablename__ = "farmer_inventory"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="quintal")
    quality_grade = Column(Enum(QualityGrade), default=QualityGrade.UNGRADED)
    harvest_date = Column(DateTime, nullable=True)
    storage_available = Column(Boolean, default=False)
    storage_cost_per_quintal_per_day = Column(Float, default=0.5)
    village = Column(String(120), nullable=True)
    district = Column(String(120), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = relationship("User", back_populates="inventory")
    crop = relationship("Crop", back_populates="inventory")
    offers = relationship("Offer", back_populates="inventory")
    quality_assessments = relationship("QualityAssessment", back_populates="inventory")
    recommendations = relationship("Recommendation", back_populates="inventory")

    __table_args__ = (
        Index("ix_inventory_farmer_crop", "farmer_id", "crop_id"),
    )


# ─────────────────────── Markets ──────────────────────────────

class MandiMarket(Base):
    __tablename__ = "mandi_markets"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(120), nullable=False)
    name_gu = Column(String(120), nullable=True)
    district = Column(String(120), nullable=False)
    state = Column(String(80), default="Gujarat")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    contact = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)

    market_prices = relationship("MarketPrice", back_populates="market")
    forecasts = relationship("Forecast", back_populates="market")

    __table_args__ = (
        Index("ix_mandi_district", "district"),
    )


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    market_id = Column(String(36), ForeignKey("mandi_markets.id"), nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    price_date = Column(DateTime, nullable=False)
    min_price = Column(Numeric(10, 2), nullable=False)
    max_price = Column(Numeric(10, 2), nullable=False)
    modal_price = Column(Numeric(10, 2), nullable=False)
    arrivals_tonnes = Column(Float, nullable=True)
    source = Column(String(80), default="demo_data")
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    market = relationship("MandiMarket", back_populates="market_prices")
    crop = relationship("Crop", back_populates="market_prices")

    __table_args__ = (
        Index("ix_price_market_crop_date", "market_id", "crop_id", "price_date"),
    )


# ─────────────────────── Forecasts ────────────────────────────

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    market_id = Column(String(36), ForeignKey("mandi_markets.id"), nullable=False)
    forecast_date = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime, nullable=False)
    horizon_days = Column(Integer, nullable=False)
    predicted_price = Column(Numeric(10, 2), nullable=False)
    lower_bound = Column(Numeric(10, 2), nullable=False)
    upper_bound = Column(Numeric(10, 2), nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(40), default="baseline_v1")
    factors = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=True)

    crop = relationship("Crop", back_populates="forecasts")
    market = relationship("MandiMarket", back_populates="forecasts")

    __table_args__ = (
        Index("ix_forecast_crop_market_horizon", "crop_id", "market_id", "horizon_days"),
    )


# ─────────────────────── Buyers ───────────────────────────────

class BuyerListing(Base):
    __tablename__ = "buyer_listings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    buyer_profile_id = Column(String(36), ForeignKey("buyer_profiles.id", ondelete="CASCADE"), nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    min_quantity = Column(Float, nullable=False)
    max_quantity = Column(Float, nullable=False)
    quality_requirement = Column(Enum(QualityGrade), default=QualityGrade.B)
    offered_price = Column(Numeric(10, 2), nullable=False)
    district = Column(String(120), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    delivery_days = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    buyer_profile = relationship("BuyerProfile", back_populates="buyer_listings")
    crop = relationship("Crop", back_populates="buyer_listings")
    offers = relationship("Offer", back_populates="buyer_listing")
    matches = relationship("BuyerMatch", back_populates="buyer_listing")

    __table_args__ = (
        Index("ix_listing_crop_active", "crop_id", "is_active"),
    )


class BuyerMatch(Base):
    __tablename__ = "buyer_matches"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farmer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    buyer_listing_id = Column(String(36), ForeignKey("buyer_listings.id"), nullable=False)
    inventory_id = Column(String(36), ForeignKey("farmer_inventory.id"), nullable=True)
    match_score = Column(Float, nullable=False)
    score_breakdown = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    buyer_listing = relationship("BuyerListing", back_populates="matches")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farmer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    buyer_listing_id = Column(String(36), ForeignKey("buyer_listings.id"), nullable=False)
    inventory_id = Column(String(36), ForeignKey("farmer_inventory.id"), nullable=True)
    offered_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(Enum(OfferStatus), default=OfferStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = relationship("User")
    buyer_listing = relationship("BuyerListing", back_populates="offers")
    inventory = relationship("FarmerInventory", back_populates="offers")


# ─────────────────────── Quality / AI ─────────────────────────

class QualityAssessment(Base):
    __tablename__ = "quality_assessments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farmer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    inventory_id = Column(String(36), ForeignKey("farmer_inventory.id"), nullable=True)
    image_url = Column(String(500), nullable=True)
    crop_type = Column(String(40), nullable=False)
    assessment_result = Column(Text, nullable=True)   # JSON string
    confidence = Column(Float, nullable=True)
    suggested_grade = Column(String(10), nullable=True)
    disclaimer = Column(Text, nullable=True)
    provider = Column(String(40), default="mock")
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="quality_assessments")
    inventory = relationship("FarmerInventory", back_populates="quality_assessments")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farmer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    inventory_id = Column(String(36), ForeignKey("farmer_inventory.id"), nullable=True)
    action = Column(Enum(RecommendationAction), nullable=False)
    recommended_days = Column(Integer, nullable=True)
    current_revenue = Column(Numeric(12, 2), nullable=True)
    expected_future_revenue = Column(Numeric(12, 2), nullable=True)
    storage_cost = Column(Numeric(10, 2), nullable=True)
    transport_cost = Column(Numeric(10, 2), nullable=True)
    quality_loss_cost = Column(Numeric(10, 2), nullable=True)
    expected_net_revenue = Column(Numeric(12, 2), nullable=True)
    potential_gain = Column(Numeric(12, 2), nullable=True)
    confidence = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    explanation_gu = Column(Text, nullable=True)
    explanation_hi = Column(Text, nullable=True)
    agent_trace = Column(Text, nullable=True)  # JSON trace of agents used
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="recommendations")
    inventory = relationship("FarmerInventory", back_populates="recommendations")


# ─────────────────────── Conversations ────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan",
                            order_by="Message.created_at")

    __table_args__ = (
        Index("ix_conv_session", "session_id"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)   # user | assistant | system
    message = Column(Text, nullable=False)
    agent_used = Column(String(80), nullable=True)
    language = Column(Enum(Language), default=Language.ENGLISH)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
