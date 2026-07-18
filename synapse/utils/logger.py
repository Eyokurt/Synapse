import logging
from typing import Any, Dict
from synapse.core.event_bus import EventBus

logger = logging.getLogger("AgentLogger")

class AgentLogger:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe("on_response", self._log_response)
        self.event_bus.subscribe("on_tool_call", self._log_tool_call)

    async def _log_response(self, response_text: str) -> None:
        logger.info(f"Agent Response: {response_text}")

    async def _log_tool_call(self, name: str, args: Dict[str, Any]) -> None:
        logger.info(f"Tool Call: {name} with args: {args}")
