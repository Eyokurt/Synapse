import pytest
from synapse.core.engine import AgentEngine
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.base import BaseLLMAdapter, LLMResponse
from typing import List, Dict, Any, Optional

class MockAdapter(BaseLLMAdapter):
    def __init__(self, mock_response: str = "", mock_responses: List[LLMResponse] = None):
        self.mock_response = mock_response
        self.mock_responses = mock_responses or []
        self.called = False
        self.call_count = 0
        self.messages = []

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        self.called = True
        self.messages = messages
        if self.mock_responses:
            if self.call_count < len(self.mock_responses):
                resp = self.mock_responses[self.call_count]
                self.call_count += 1
                return resp
            return LLMResponse(content="Fallback response")
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

@pytest.mark.asyncio
async def test_agent_engine_agentic_loop():
    memory = Memory()
    event_bus = EventBus()
    tool_registry = ToolRegistry()
    
    async def get_weather(location: str):
        return f"Weather in {location} is sunny."
    tool_registry.register(get_weather, "Get weather")
    
    resp1 = LLMResponse(
        content=None,
        tool_calls=[{
            "id": "call_123",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "London"}'
            }
        }]
    )
    resp2 = LLMResponse(content="The weather in London is sunny.")
    
    llm = MockAdapter(mock_responses=[resp1, resp2])

    engine = AgentEngine(
        llm=llm,
        memory=memory,
        event_bus=event_bus,
        tool_registry=tool_registry,
        max_iterations=5
    )

    events_emitted = []
    def on_response_handler(text):
        events_emitted.append(text)

    event_bus.subscribe("on_response", on_response_handler)

    response = await engine.process("What's the weather in London?", agentic_mode=True)

    assert response == "The weather in London is sunny."
    assert llm.call_count == 2
    
    msgs = memory.get_messages()
    assert len(msgs) == 4
    assert msgs[0] == {"role": "user", "content": "What's the weather in London?"}
    assert msgs[1] == {
        "role": "assistant",
        "content": "",
        "tool_calls": resp1.tool_calls
    }
    assert msgs[2] == {
        "role": "tool",
        "content": "Weather in London is sunny.",
        "tool_call_id": "call_123"
    }
    assert msgs[3] == {
        "role": "assistant",
        "content": "The weather in London is sunny."
    }

    assert events_emitted == ["The weather in London is sunny."]

@pytest.mark.asyncio
async def test_agent_engine_max_iterations():
    memory = Memory()
    event_bus = EventBus()
    tool_registry = ToolRegistry()
    
    resp1 = LLMResponse(
        content=None,
        tool_calls=[{
            "id": "call_123",
            "function": {
                "name": "dummy",
                "arguments": '{}'
            }
        }]
    )
    
    llm = MockAdapter(mock_responses=[resp1] * 5)
    
    engine = AgentEngine(
        llm=llm,
        memory=memory,
        event_bus=event_bus,
        tool_registry=tool_registry,
        max_iterations=3
    )
    
    with pytest.raises(RuntimeError, match="Max iterations"):
        await engine.process("Loop forever", agentic_mode=True)
