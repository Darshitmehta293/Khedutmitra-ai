"""
Agent 4: Direct Buyer-Farmer Matching Agent
Weighted multi-factor matching engine.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent, AgentResult
from app.services.market_data_provider import DEMO_MARKETS
from app.core.logging import logger


# Demo buyer listings — in production these come from the database
DEMO_BUYERS = [
    {
        "id": "buyer_1",
        "business_name": "Shree Ram Cotton Ginners",
        "buyer_type": "ginning_mill",
        "crop_id": "crop_cotton",
        "district": "Ahmedabad",
        "min_quantity": 20, "max_quantity": 500,
        "quality_requirement": "A",
        "offered_price": 7150,
        "delivery_days": 2,
        "lat": 23.0225, "lon": 72.5714,
        "contact_phone": "+91-79-XXXXXXXX",
        "is_demo": True,
    },
    {
        "id": "buyer_2",
        "business_name": "Gujarat Cotton Traders Pvt. Ltd.",
        "buyer_type": "trader",
        "crop_id": "crop_cotton",
        "district": "Rajkot",
        "min_quantity": 10, "max_quantity": 200,
        "quality_requirement": "B",
        "offered_price": 7020,
        "delivery_days": 3,
        "lat": 22.3039, "lon": 70.8022,
        "contact_phone": "+91-281-XXXXXXX",
        "is_demo": True,
    },
    {
        "id": "buyer_3",
        "business_name": "Amreli Ginning & Pressing Co.",
        "buyer_type": "ginning_mill",
        "crop_id": "crop_cotton",
        "district": "Amreli",
        "min_quantity": 5, "max_quantity": 100,
        "quality_requirement": "B",
        "offered_price": 6950,
        "delivery_days": 2,
        "lat": 21.6032, "lon": 71.2173,
        "contact_phone": "+91-2792-XXXXXX",
        "is_demo": True,
    },
    {
        "id": "buyer_4",
        "business_name": "Saurashtra Groundnut Oil Mill",
        "buyer_type": "oil_mill",
        "crop_id": "crop_groundnut",
        "district": "Junagadh",
        "min_quantity": 50, "max_quantity": 1000,
        "quality_requirement": "B",
        "offered_price": 5950,
        "delivery_days": 3,
        "lat": 21.5222, "lon": 70.4579,
        "contact_phone": "+91-285-XXXXXXX",
        "is_demo": True,
    },
    {
        "id": "buyer_5",
        "business_name": "Gondal Groundnut Processors",
        "buyer_type": "processor",
        "crop_id": "crop_groundnut",
        "district": "Rajkot",
        "min_quantity": 20, "max_quantity": 300,
        "quality_requirement": "A",
        "offered_price": 6000,
        "delivery_days": 2,
        "lat": 21.9610, "lon": 70.8002,
        "contact_phone": "+91-2825-XXXXXX",
        "is_demo": True,
    },
    {
        "id": "buyer_6",
        "business_name": "Bhavnagar Cotton Export House",
        "buyer_type": "exporter",
        "crop_id": "crop_cotton",
        "district": "Bhavnagar",
        "min_quantity": 100, "max_quantity": 2000,
        "quality_requirement": "A",
        "offered_price": 7200,
        "delivery_days": 5,
        "lat": 21.7645, "lon": 72.1519,
        "contact_phone": "+91-278-XXXXXXX",
        "is_demo": True,
    },
]

GRADE_ORDER = {"A": 3, "B": 2, "C": 1, "ungraded": 0}

SCORE_WEIGHTS = {
    "crop_match": 0.25,
    "quantity_compat": 0.20,
    "quality_compat": 0.15,
    "price_compat": 0.20,
    "distance": 0.10,
    "timing": 0.10,
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _farmer_coords(district: str):
    for m in DEMO_MARKETS:
        if m["district"].lower() == district.lower():
            return m["lat"], m["lon"]
    return 22.3, 71.0  # Gujarat centroid fallback


class BuyerMatchingAgent(BaseAgent):
    name = "BuyerMatchingAgent"

    def __init__(self, buyers: Optional[List[Dict]] = None):
        self.buyers = buyers or DEMO_BUYERS

    async def run(self, crop_id: str, quantity: float, quality_grade: str,
                  district: str, preferred_price: Optional[float] = None,
                  **kwargs) -> AgentResult:
        logger.info("BuyerMatchingAgent running", crop_id=crop_id, quantity=quantity, district=district)

        farmer_lat, farmer_lon = _farmer_coords(district)
        farmer_grade_val = GRADE_ORDER.get(quality_grade, 1)
        matches = []

        buyers = kwargs.get("buyers") or self.buyers
        for buyer in buyers:
            breakdown: Dict[str, float] = {}

            # Crop match (hard filter + partial)
            if buyer["crop_id"] != crop_id:
                continue
            breakdown["crop_match"] = 1.0

            # Quantity compatibility
            if quantity < buyer["min_quantity"]:
                qty_score = 0.4 * (quantity / buyer["min_quantity"])
            elif quantity > buyer["max_quantity"]:
                qty_score = 0.5
            else:
                qty_score = 1.0
            breakdown["quantity_compat"] = qty_score

            # Quality compatibility
            buyer_grade_val = GRADE_ORDER.get(buyer["quality_requirement"], 1)
            if farmer_grade_val >= buyer_grade_val:
                qual_score = 1.0
            else:
                qual_score = max(0.0, 1.0 - (buyer_grade_val - farmer_grade_val) * 0.4)
            breakdown["quality_compat"] = qual_score

            # Price compatibility
            ref_price = preferred_price or buyer["offered_price"]
            price_diff_pct = abs(buyer["offered_price"] - ref_price) / ref_price if ref_price > 0 else 0
            price_score = max(0.0, 1.0 - price_diff_pct * 3)
            breakdown["price_compat"] = round(price_score, 3)

            # Distance score (closer = better, 200km = 0 score)
            dist_km = _haversine_km(farmer_lat, farmer_lon, buyer["lat"], buyer["lon"])
            dist_score = max(0.0, 1.0 - dist_km / 200)
            breakdown["distance"] = round(dist_score, 3)

            # Timing (delivery_days ≤ 3 is best)
            timing_score = 1.0 if buyer["delivery_days"] <= 3 else max(0.2, 1.0 - (buyer["delivery_days"] - 3) * 0.15)
            breakdown["timing"] = round(timing_score, 3)

            # Weighted total
            total_score = sum(breakdown[k] * SCORE_WEIGHTS[k] for k in breakdown if k in SCORE_WEIGHTS)
            total_score = round(total_score * 100, 1)

            reason = self._build_reason(breakdown, buyer, dist_km, quality_grade)

            matches.append({
                "listing_id": buyer["id"],
                "buyer_name": buyer["business_name"],
                "buyer_type": buyer["buyer_type"],
                "crop_name": crop_id.replace("crop_", "").title(),
                "offered_price": buyer["offered_price"],
                "min_quantity": buyer["min_quantity"],
                "max_quantity": buyer["max_quantity"],
                "quality_requirement": buyer["quality_requirement"],
                "district": buyer["district"],
                "distance_km": round(dist_km, 1),
                "delivery_days": buyer["delivery_days"],
                "match_score": total_score,
                "score_breakdown": breakdown,
                "reason": reason,
                "contact_phone": buyer.get("contact_phone"),
                "is_demo": buyer.get("is_demo", True),
            })

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        top_matches = matches[:5]

        return AgentResult(self.name, True, {
            "crop_id": crop_id,
            "quantity": quantity,
            "quality_grade": quality_grade,
            "district": district,
            "matches": top_matches,
            "total_found": len(matches),
            "best_buyer": top_matches[0] if top_matches else None,
        })

    def _build_reason(self, breakdown: Dict, buyer: Dict, dist_km: float, farmer_grade: str) -> str:
        parts = []
        if breakdown.get("crop_match", 0) >= 1.0:
            parts.append("Exact crop match")
        if breakdown.get("quantity_compat", 0) >= 0.8:
            parts.append("Good quantity fit")
        if breakdown.get("quality_compat", 0) >= 0.8:
            parts.append(f"Accepts {farmer_grade} grade")
        if breakdown.get("price_compat", 0) >= 0.7:
            parts.append(f"Competitive price ₹{buyer['offered_price']:,}")
        if dist_km < 80:
            parts.append(f"Nearby ({dist_km:.0f}km)")
        return "; ".join(parts) if parts else "Partial match"
