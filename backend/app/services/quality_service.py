"""
KhedutMitra AI — Quality Assessment Service Abstraction

Provider pattern: MockQualityProvider → VisionModelProvider → FutureProductionProvider.
"""
from __future__ import annotations
import abc
import random
from typing import Any, Dict, Optional
from app.core.logging import logger

DISCLAIMER = (
    "AI-assisted preliminary assessment only. "
    "Final quality determination should follow applicable buyer/market testing standards. "
    "This is NOT an official commercial grade or certification."
)


class QualityAssessmentService(abc.ABC):
    @abc.abstractmethod
    async def assess(self, crop_type: str, image_url: Optional[str] = None,
                     image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        ...


COTTON_INDICATORS = {
    "color": ["White", "Creamy White", "Off-White", "Yellowish"],
    "contamination_level": ["None visible", "Minimal", "Low", "Moderate"],
    "cleanliness": ["Very Clean", "Clean", "Mostly Clean", "Mixed"],
    "fiber_length_visual": ["Long staple apparent", "Medium staple apparent", "Short staple apparent"],
}

GROUNDNUT_INDICATORS = {
    "kernel_condition": ["Plump & Uniform", "Mostly Uniform", "Mixed sizes", "Some shriveled"],
    "discoloration": ["None visible", "Minimal", "Slight", "Moderate"],
    "damaged_kernels_pct": ["<2%", "2–5%", "5–10%", ">10%"],
    "foreign_matter": ["None visible", "Trace", "Minimal"],
}

GRADE_PROFILES = {
    "A": {"confidence_range": (0.78, 0.91), "score": 0},
    "B": {"confidence_range": (0.65, 0.80), "score": 1},
    "C": {"confidence_range": (0.55, 0.72), "score": 2},
}


class MockQualityProvider(QualityAssessmentService):
    """Returns a realistic mock quality assessment. Clearly labeled as mock."""

    async def assess(self, crop_type: str, image_url: Optional[str] = None,
                     image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        rng = random.Random()
        grade = rng.choices(["A", "B", "C"], weights=[0.45, 0.40, 0.15])[0]
        conf_range = GRADE_PROFILES[grade]["confidence_range"]
        confidence = round(rng.uniform(*conf_range), 3)

        if crop_type.lower() == "cotton":
            grade_idx = ord(grade) - ord("A")
            details = {
                "color": COTTON_INDICATORS["color"][min(grade_idx, len(COTTON_INDICATORS["color"])-1)],
                "contamination_level": COTTON_INDICATORS["contamination_level"][grade_idx],
                "cleanliness": COTTON_INDICATORS["cleanliness"][grade_idx],
                "fiber_length_visual": rng.choice(COTTON_INDICATORS["fiber_length_visual"]),
                "visual_notes": (
                    "Visually appears to be good-quality lint cotton with minimal trash."
                    if grade == "A" else
                    "Some visible impurities detected. Manual sorting recommended before ginning."
                ),
            }
        else:
            grade_idx = ord(grade) - ord("A")
            details = {
                "kernel_condition": GROUNDNUT_INDICATORS["kernel_condition"][grade_idx],
                "discoloration": GROUNDNUT_INDICATORS["discoloration"][grade_idx],
                "estimated_damaged_kernels": GROUNDNUT_INDICATORS["damaged_kernels_pct"][grade_idx],
                "foreign_matter": GROUNDNUT_INDICATORS["foreign_matter"][min(grade_idx, 2)],
                "visual_notes": (
                    "Kernels appear uniform with good fill. Low visible damage."
                    if grade == "A" else
                    "Some size variation noted. Some visible discoloration."
                ),
            }

        return {
            "suggested_grade": grade,
            "confidence": confidence,
            "crop_type": crop_type,
            "assessment_details": details,
            "disclaimer": DISCLAIMER,
            "provider": "mock",
            "is_demo": True,
        }


def get_quality_provider(enable_ai: bool = False) -> QualityAssessmentService:
    if enable_ai:
        # Future: return VisionModelProvider()
        logger.warning("Quality AI not yet implemented, falling back to mock")
    return MockQualityProvider()
