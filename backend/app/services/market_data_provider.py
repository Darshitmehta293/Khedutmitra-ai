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
import httpx
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


class AGMARKNETProvider(MarketDataProvider):
    """Adapter for AGMARKNET-compatible JSON endpoints with safe fallback."""

    def __init__(self, endpoint: str, api_key: Optional[str], fallback: MarketDataProvider):
        self.endpoint = endpoint
        self.api_key = api_key
        self.fallback = fallback

    @staticmethod
    def _number(value: Any, default: float = 0.0) -> float:
        try:
            return float(str(value).replace(",", "").strip())
        except (TypeError, ValueError):
            return default

    def _normalize(self, item: Dict[str, Any], crop_id: str, market_id: Optional[str]) -> Optional[MarketPriceData]:
        market = str(item.get("market_id") or item.get("market") or market_id or "unknown")
        modal = self._number(item.get("modal_price") or item.get("modal_price_rs"))
        minimum = self._number(item.get("min_price") or item.get("min_price_rs"), modal)
        maximum = self._number(item.get("max_price") or item.get("max_price_rs"), modal)
        if modal <= 0 or minimum <= 0 or maximum <= 0:
            return None
        date_value = item.get("price_date") or item.get("arrival_date")
        try:
            price_date = datetime.fromisoformat(str(date_value).replace("Z", "+00:00")) if date_value else datetime.utcnow()
        except ValueError:
            price_date = datetime.utcnow()
        return MarketPriceData(
            market_id=market,
            market_name=str(item.get("market_name") or item.get("market") or market),
            crop_id=crop_id,
            crop_name=str(item.get("crop_name") or crop_id.replace("crop_", "").title()),
            price_date=price_date,
            min_price=minimum,
            max_price=maximum,
            modal_price=modal,
            arrivals_tonnes=self._number(item.get("arrivals_tonnes") or item.get("arrivals")),
            source="agmarknet",
            is_demo=False,
        )

    async def _fetch(self, crop_id: str, market_id: Optional[str] = None) -> List[MarketPriceData]:
        params = {"crop_id": crop_id}
        if market_id:
            params["market_id"] = market_id
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(self.endpoint, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
        rows = payload.get("data", payload) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError("Market provider response must contain a data list")
        return [normalized for row in rows if isinstance(row, dict) for normalized in [self._normalize(row, crop_id, market_id)] if normalized]

    async def get_current_prices(self, crop_id: str, market_id: Optional[str] = None) -> List[MarketPriceData]:
        try:
            prices = await self._fetch(crop_id, market_id)
            return prices or await self.fallback.get_current_prices(crop_id, market_id)
        except Exception as exc:
            logger.warning("Live market provider unavailable; using fallback", error=str(exc))
            return await self.fallback.get_current_prices(crop_id, market_id)

    async def get_historical_prices(self, crop_id: str, market_id: str, days: int = 30) -> List[MarketPriceData]:
        return await self.get_current_prices(crop_id, market_id)

    async def get_market_list(self, district: Optional[str] = None) -> List[Dict[str, Any]]:
        return await self.fallback.get_market_list(district)

    async def health_check(self) -> Dict[str, Any]:
        try:
            await self._fetch("crop_cotton")
            return {"status": "ok", "provider": "agmarknet", "is_demo": False}
        except Exception as exc:
            return {"status": "degraded", "provider": "agmarknet", "is_demo": True, "error": str(exc)}


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
    if provider_type in {"agmarknet", "live"}:
        from app.core.config import settings
        fallback = MockMarketDataProvider()
        if settings.LIVE_MARKET_DATA_API_URL:
            return AGMARKNETProvider(settings.LIVE_MARKET_DATA_API_URL, settings.LIVE_MARKET_DATA_API_KEY, fallback)
        logger.warning("Live market provider requested without endpoint; falling back to mock")
        return fallback
    logger.warning("Unknown market data provider, falling back to mock", provider=provider_type)
    return MockMarketDataProvider()
