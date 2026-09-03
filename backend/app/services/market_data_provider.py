"""
KhedutMitra AI — Market Data Provider Abstraction

Production-ready interface. Swap MockMarketDataProvider for a live
AGMARKNET or state APMC API provider without changing any agent code.
"""
from __future__ import annotations
import abc
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.core.logging import logger


# ─────────────────────── Data Classes ─────────────────────────

class MarketPriceData:
    def __init__(self, market_id: str, market_name: str, crop_id: str, crop_name: str,
                 price_date: datetime, min_price: float, max_price: float,
                 modal_price: float, arrivals_tonnes: float, source: str, is_demo: bool):
        self.market_id = market_id
        self.market_name = market_name
        self.crop_id = crop_id
        self.crop_name = crop_name
        self.price_date = price_date
        self.min_price = min_price
        self.max_price = max_price
        self.modal_price = modal_price
        self.arrivals_tonnes = arrivals_tonnes
        self.source = source
        self.is_demo = is_demo

    def to_dict(self) -> Dict[str, Any]:
        return {
            "market_id": self.market_id,
            "market_name": self.market_name,
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "price_date": self.price_date.isoformat(),
            "min_price": self.min_price,
            "max_price": self.max_price,
            "modal_price": self.modal_price,
            "arrivals_tonnes": self.arrivals_tonnes,
            "source": self.source,
            "is_demo": self.is_demo,
        }


# ─────────────────────── Abstract Base ────────────────────────

class MarketDataProvider(abc.ABC):
    """Abstract market data provider — swap implementations freely."""

    @abc.abstractmethod
    async def get_current_prices(self, crop_id: str, market_id: Optional[str] = None) -> List[MarketPriceData]:
        ...

    @abc.abstractmethod
    async def get_historical_prices(self, crop_id: str, market_id: str, days: int = 30) -> List[MarketPriceData]:
        ...

    @abc.abstractmethod
    async def get_market_list(self, district: Optional[str] = None) -> List[Dict[str, Any]]:
        ...

    @abc.abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        ...


# ─────────────────────── Mock Provider ────────────────────────

# Realistic Gujarat mandi base prices (₹/quintal) — demo data
DEMO_BASE_PRICES: Dict[str, Dict[str, float]] = {
    "cotton": {
        "ahmedabad": 7050,
        "rajkot": 6980,
        "junagadh": 6900,
        "gondal": 7100,
        "bhavnagar": 6950,
        "amreli": 6870,
        "surendranagar": 7020,
        "anand": 7080,
    },
    "groundnut": {
        "ahmedabad": 5800,
        "rajkot": 5750,
        "junagadh": 5900,
        "gondal": 5820,
        "bhavnagar": 5760,
        "amreli": 5840,
        "surendranagar": 5780,
        "anand": 5810,
    },
}

DEMO_MARKETS = [
    {"id": "mkt_ahmedabad", "name": "Ahmedabad APMC", "name_gu": "અમદાવાદ APMC", "district": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714},
    {"id": "mkt_rajkot",    "name": "Rajkot APMC",    "name_gu": "રાજકોટ APMC",    "district": "Rajkot",    "state": "Gujarat", "lat": 22.3039, "lon": 70.8022},
    {"id": "mkt_junagadh",  "name": "Junagadh APMC",  "name_gu": "જૂનાગઢ APMC",   "district": "Junagadh",  "state": "Gujarat", "lat": 21.5222, "lon": 70.4579},
    {"id": "mkt_gondal",    "name": "Gondal APMC",    "name_gu": "ગોંડલ APMC",    "district": "Rajkot",    "state": "Gujarat", "lat": 21.9610, "lon": 70.8002},
    {"id": "mkt_bhavnagar", "name": "Bhavnagar APMC", "name_gu": "ભાવનગર APMC",  "district": "Bhavnagar", "state": "Gujarat", "lat": 21.7645, "lon": 72.1519},
    {"id": "mkt_amreli",    "name": "Amreli APMC",    "name_gu": "અમરેલી APMC",   "district": "Amreli",    "state": "Gujarat", "lat": 21.6032, "lon": 71.2173},
    {"id": "mkt_surendranagar", "name": "Surendranagar APMC", "name_gu": "સુરેન્દ્રનગર APMC", "district": "Surendranagar", "state": "Gujarat", "lat": 22.7279, "lon": 71.6493},
    {"id": "mkt_anand",     "name": "Anand APMC",     "name_gu": "આણંદ APMC",     "district": "Anand",     "state": "Gujarat", "lat": 22.5645, "lon": 72.9289},
]

DEMO_CROPS = {
    "crop_cotton":    {"name": "Cotton",    "name_gu": "કપાસ",    "name_hi": "कपास",    "category": "cotton"},
    "crop_groundnut": {"name": "Groundnut", "name_gu": "મગફળી",   "name_hi": "मूंगफली", "category": "groundnut"},
}


class MockMarketDataProvider(MarketDataProvider):
    """
    Realistic demo data provider using seeded Gujarat market prices.
    All data is clearly marked is_demo=True.
    """

    def _market_key(self, market_id: str) -> str:
        return market_id.replace("mkt_", "").lower()

    def _crop_key(self, crop_id: str) -> str:
        return crop_id.replace("crop_", "").lower()

    def _base_price(self, crop_id: str, market_id: str) -> float:
        ck = self._crop_key(crop_id)
        mk = self._market_key(market_id)
        prices = DEMO_BASE_PRICES.get(ck, {})
        return prices.get(mk, list(prices.values())[0] if prices else 6500)

    def _daily_variation(self, base: float, seed: int, day_offset: int) -> float:
        rng = random.Random(seed + day_offset * 37)
        pct = rng.uniform(-0.022, 0.028)
        return round(base * (1 + pct), 2)

    async def get_current_prices(self, crop_id: str, market_id: Optional[str] = None) -> List[MarketPriceData]:
        markets = [m for m in DEMO_MARKETS if market_id is None or m["id"] == market_id]
        results = []
        today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        for m in markets:
            base = self._base_price(crop_id, m["id"])
            modal = self._daily_variation(base, hash(m["id"] + crop_id), 0)
            results.append(MarketPriceData(
                market_id=m["id"], market_name=m["name"],
                crop_id=crop_id, crop_name=DEMO_CROPS.get(crop_id, {}).get("name", crop_id),
                price_date=today,
                min_price=round(modal * 0.965, 2),
                max_price=round(modal * 1.023, 2),
                modal_price=modal,
                arrivals_tonnes=round(random.Random(hash(m["id"])).uniform(80, 600), 1),
                source="demo_data",
                is_demo=True,
            ))
        return results

    async def get_historical_prices(self, crop_id: str, market_id: str, days: int = 30) -> List[MarketPriceData]:
        results = []
        base = self._base_price(crop_id, market_id)
        market_name = next((m["name"] for m in DEMO_MARKETS if m["id"] == market_id), market_id)
        crop_name = DEMO_CROPS.get(crop_id, {}).get("name", crop_id)
        today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        seed_base = hash(market_id + crop_id)

        # build a slow-moving trend + seasonality for realism
        for i in range(days, 0, -1):
            day = today - timedelta(days=i)
            # trend: slight upward over 30 days
            trend_factor = 1 + (days - i) * 0.0008
            modal = self._daily_variation(base * trend_factor, seed_base, i)
            results.append(MarketPriceData(
                market_id=market_id, market_name=market_name,
                crop_id=crop_id, crop_name=crop_name,
                price_date=day,
                min_price=round(modal * 0.965, 2),
                max_price=round(modal * 1.023, 2),
                modal_price=modal,
                arrivals_tonnes=round(random.Random(seed_base + i).uniform(80, 600), 1),
                source="demo_data",
                is_demo=True,
            ))
        return results

    async def get_market_list(self, district: Optional[str] = None) -> List[Dict[str, Any]]:
        if district:
            return [m for m in DEMO_MARKETS if m["district"].lower() == district.lower()]
        return DEMO_MARKETS

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": "mock", "is_demo": True}


# ─────────────────────── Factory ──────────────────────────────

def get_market_data_provider(provider_type: str = "mock") -> MarketDataProvider:
    if provider_type == "mock":
        return MockMarketDataProvider()
    # Future: LiveMarketDataProvider, AGMARKNETProvider etc.
    logger.warning("Unknown market data provider, falling back to mock", provider=provider_type)
    return MockMarketDataProvider()
