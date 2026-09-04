"""
KhedutMitra AI — Pydantic Schemas (request/response models)
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, validator

from app.models.models import (
    UserRole, Language, CropCategory, QualityGrade,
    RecommendationAction, OfferStatus, BuyerType
)


# ─────────────────────── Auth ─────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.FARMER
    language: Language = Language.GUJARATI
    location: Optional[str] = None
    # Farmer extras
    village: Optional[str] = None
    district: Optional[str] = None
    # Buyer extras
    business_name: Optional[str] = None
    buyer_type: Optional[BuyerType] = None


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: str
    name: str
    language: Language = Language.ENGLISH


class UserOut(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str]
    role: UserRole
    language: Language
    location: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────── Farmer Profile ───────────────────────

class FarmerProfileOut(BaseModel):
    id: str
    village: Optional[str]
    district: Optional[str]
    state: str
    farm_size_acres: Optional[float]

    class Config:
        from_attributes = True


# ─────────────────────── Inventory ────────────────────────────

class InventoryCreate(BaseModel):
    crop_id: str
    quantity: float = Field(..., gt=0, description="Quantity in quintals")
    quality_grade: QualityGrade = QualityGrade.UNGRADED
    harvest_date: Optional[datetime] = None
    storage_available: bool = False
    storage_cost_per_quintal_per_day: float = Field(default=0.5, ge=0)
    village: Optional[str] = None
    district: Optional[str] = None
    notes: Optional[str] = None


class InventoryUpdate(BaseModel):
    quantity: Optional[float] = None
    quality_grade: Optional[QualityGrade] = None
    storage_available: Optional[bool] = None
    storage_cost_per_quintal_per_day: Optional[float] = None
    notes: Optional[str] = None


class CropOut(BaseModel):
    id: str
    name: str
    name_gu: Optional[str]
    name_hi: Optional[str]
    category: CropCategory
    unit: str

    class Config:
        from_attributes = True


class InventoryOut(BaseModel):
    id: str
    farmer_id: str
    crop: CropOut
    quantity: float
    unit: str
    quality_grade: QualityGrade
    harvest_date: Optional[datetime]
    storage_available: bool
    storage_cost_per_quintal_per_day: float
    village: Optional[str]
    district: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────── Markets ──────────────────────────────

class MandiMarketOut(BaseModel):
    id: str
    name: str
    name_gu: Optional[str]
    district: str
    state: str
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True


class MarketPriceOut(BaseModel):
    id: str
    market: MandiMarketOut
    crop: CropOut
    price_date: datetime
    min_price: float
    max_price: float
    modal_price: float
    arrivals_tonnes: Optional[float]
    source: str
    is_demo: bool

    class Config:
        from_attributes = True


class PriceTrendOut(BaseModel):
    crop_id: str
    market_id: str
    crop_name: str
    market_name: str
    current_price: float
    min_price: float
    max_price: float
    trend: str  # upward | downward | stable
    trend_percentage: float
    data_timestamp: str
    source: str
    confidence: float
    is_demo: bool
    prices_7d: List[Dict[str, Any]]


# ─────────────────────── Forecasts ────────────────────────────

class ForecastOut(BaseModel):
    crop_id: str
    market_id: str
    crop_name: str
    market_name: str
    horizon_days: int
    target_date: str
    predicted_price: float
    lower_bound: float
    upper_bound: float
    confidence: float
    model_version: str
    factors: Optional[str]
    is_demo: bool
    disclaimer: str = "Forecasts are estimates. Actual market prices may differ significantly."


class ForecastSeriesOut(BaseModel):
    crop_id: str
    market_id: str
    forecasts: List[ForecastOut]
    is_demo: bool


# ─────────────────────── Recommendation ──────────────────────

class RecommendationRequest(BaseModel):
    crop_id: str
    quantity: float = Field(..., gt=0)
    quality_grade: QualityGrade = QualityGrade.B
    district: str
    storage_available: bool = False
    storage_cost_per_quintal_per_day: float = 0.5
    transport_cost_total: float = 2000.0
    horizon_days: int = 7
    inventory_id: Optional[str] = None


class RecommendationOut(BaseModel):
    action: RecommendationAction
    recommended_days: Optional[int]
    current_price: float
    current_revenue: float
    forecast_price: float
    expected_future_revenue: float
    storage_cost: float
    transport_cost: float
    quality_loss_cost: float
    expected_net_revenue: float
    potential_gain: float
    confidence: float
    reasoning: str
    best_buyer: Optional[Dict[str, Any]]
    agent_trace: List[Dict[str, Any]]
    is_demo: bool


# ─────────────────────── Buyer / Matching ─────────────────────

class BuyerListingCreate(BaseModel):
    crop_id: str
    min_quantity: float = Field(..., gt=0)
    max_quantity: float = Field(..., gt=0)
    quality_requirement: QualityGrade = QualityGrade.B
    offered_price: float = Field(..., gt=0)
    district: Optional[str] = None
    delivery_days: int = 3


class BuyerProfileCreate(BaseModel):
    business_name: str = Field(..., min_length=2)
    buyer_type: BuyerType
    address: Optional[str] = None
    district: Optional[str] = None
    gst_number: Optional[str] = None


class BuyerListingOut(BaseModel):
    id: str
    buyer_profile: Dict[str, Any]
    crop: CropOut
    min_quantity: float
    max_quantity: float
    quality_requirement: QualityGrade
    offered_price: float
    district: Optional[str]
    delivery_days: int
    is_active: bool
    is_demo: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BuyerMatchOut(BaseModel):
    listing_id: str
    buyer_name: str
    buyer_type: str
    crop_name: str
    offered_price: float
    min_quantity: float
    max_quantity: float
    quality_requirement: str
    district: Optional[str]
    delivery_days: int
    match_score: float
    score_breakdown: Dict[str, float]
    reason: str
    contact_phone: Optional[str]
    is_demo: bool


class BuyerMatchRequest(BaseModel):
    crop_id: str
    quantity: float
    quality_grade: QualityGrade
    district: str
    preferred_price: Optional[float] = None


# ─────────────────────── Offers ───────────────────────────────

class OfferCreate(BaseModel):
    buyer_listing_id: str
    inventory_id: Optional[str] = None
    quantity: float = Field(..., gt=0)
    offered_price: float = Field(..., gt=0)
    message: Optional[str] = None


class OfferOut(BaseModel):
    id: str
    farmer_id: str
    buyer_listing_id: str
    quantity: float
    offered_price: float
    message: Optional[str]
    status: OfferStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────── Quality ──────────────────────────────

class QualityAssessmentOut(BaseModel):
    id: str
    crop_type: str
    suggested_grade: Optional[str]
    confidence: Optional[float]
    assessment_result: Dict[str, Any]
    disclaimer: str
    provider: str
    created_at: datetime


# ─────────────────────── AI / Chat ────────────────────────────

class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str
    language: Language = Language.ENGLISH


class ChatRequest(BaseModel):
    message: str
    language: Language = Language.ENGLISH
    session_id: Optional[str] = None
    crop_id: Optional[str] = None
    quantity: Optional[float] = None
    district: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    language: Language
    intent: Optional[str]
    agent_trace: List[Dict[str, Any]]
    structured_data: Optional[Dict[str, Any]]
    session_id: str
    is_demo: bool


# ─────────────────────── Dashboard ────────────────────────────

class DashboardOut(BaseModel):
    farmer_name: str
    district: Optional[str]
    total_inventory_quintals: float
    cotton_quintals: float
    groundnut_quintals: float
    current_estimated_value: float
    expected_value_7d: float
    potential_gain: float
    active_buyer_opportunities: int
    latest_recommendation: Optional[RecommendationOut]
    top_prices: List[PriceTrendOut]
    recent_conversations: int
    is_demo: bool


# ─────────────────────── Admin ────────────────────────────────

class SystemHealthOut(BaseModel):
    status: str
    database: str
    ai_service: str
    market_data_provider: str
    granite_configured: bool
    demo_mode: bool
    version: str
    timestamp: str
