import pytest
from synapse.core.engine import AgentEngine
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.base import BaseLLMAdapter, LLMResponse
from typing import List, Dict, Any, Optional

class MockAdapter(BaseLLMAdapter):
    def __init__(self, mock_response: str):
        self.mock_response = mock_response
        self.called = False
        self.messages = []

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        self.called = True
        self.messages = messages
        return LLMResponse(content=self.mock_response)

@pytest.mark.asyncio
async def test_agent_engine_process():
    memory = Memory()
    event_bus = EventBus()
    tool_registry = ToolRegistry()
    llm = MockAdapter(mock_response="Hello User!")

    engine = AgentEngine(
        llm=llm,
        memory=memory,
        event_bus=event_bus,
        tool_registry=tool_registry
    )

    events_emitted = []
    def on_response_handler(text):
        events_emitted.append(text)

    event_bus.subscribe("on_response", on_response_handler)

    response = await engine.process("Hi")

    assert response == "Hello User!"
    assert llm.called
    
    msgs = memory.get_messages()
    assert len(msgs) == 2
    assert msgs[0] == {"role": "user", "content": "Hi"}
    assert msgs[1] == {"role": "assistant", "content": "Hello User!"}

    assert events_emitted == ["Hello User!"]
