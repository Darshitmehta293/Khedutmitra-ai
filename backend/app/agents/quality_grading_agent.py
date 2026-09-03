"""
Agent 5: Quality Grading Assistance Agent
Wraps the QualityAssessmentService with agent interface.
"""
from __future__ import annotations
from typing import Optional

from app.agents.base import BaseAgent, AgentResult
from app.services.quality_service import QualityAssessmentService
from app.core.logging import logger


class QualityGradingAgent(BaseAgent):
    name = "QualityGradingAgent"

    def __init__(self, quality_service: QualityAssessmentService):
        self.quality_service = quality_service

    async def run(self, crop_type: str, image_url: Optional[str] = None,
                  image_bytes: Optional[bytes] = None, **kwargs) -> AgentResult:
        logger.info("QualityGradingAgent running", crop_type=crop_type)
        try:
            result = await self.quality_service.assess(crop_type, image_url, image_bytes)
            return AgentResult(self.name, True, result)
        except Exception as e:
            logger.error("QualityGradingAgent error", error=str(e))
            return AgentResult(self.name, False, {}, str(e))
