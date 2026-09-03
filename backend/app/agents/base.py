"""
KhedutMitra AI — Agent Base Interface
"""
from __future__ import annotations
import abc
import time
from typing import Any, Dict


class AgentResult:
    def __init__(self, agent_name: str, success: bool, data: Dict[str, Any],
                 error: str = "", latency_ms: float = 0.0):
        self.agent_name = agent_name
        self.success = success
        self.data = data
        self.error = error
        self.latency_ms = latency_ms

    def to_trace(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "status": "✓ success" if self.success else "✗ failed",
            "latency_ms": round(self.latency_ms, 1),
            "error": self.error if not self.success else None,
        }


class BaseAgent(abc.ABC):
    name: str = "base_agent"

    @abc.abstractmethod
    async def run(self, **kwargs) -> AgentResult:
        ...

    async def _timed_run(self, **kwargs) -> AgentResult:
        t0 = time.perf_counter()
        try:
            result = await self.run(**kwargs)
            result.latency_ms = (time.perf_counter() - t0) * 1000
            return result
        except Exception as e:
            return AgentResult(
                agent_name=self.name, success=False, data={},
                error=str(e), latency_ms=(time.perf_counter() - t0) * 1000
            )
