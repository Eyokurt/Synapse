import pytest
import logging
from synapse.core.event_bus import EventBus
from synapse.utils.logger import AgentLogger

@pytest.mark.asyncio
async def test_agent_logger_on_response(caplog):
    caplog.set_level(logging.INFO, logger="AgentLogger")
    event_bus = EventBus()
    agent_logger = AgentLogger(event_bus)
    
    await event_bus.emit("on_response", "Hello world")
    
    assert "Agent Response: Hello world" in caplog.text

@pytest.mark.asyncio
async def test_agent_logger_on_tool_call(caplog):
    caplog.set_level(logging.INFO, logger="AgentLogger")
    event_bus = EventBus()
    agent_logger = AgentLogger(event_bus)
    
    await event_bus.emit("on_tool_call", "my_tool", {"arg1": 123})
    
    assert "Tool Call: my_tool with args: {'arg1': 123}" in caplog.text
