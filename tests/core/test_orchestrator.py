import pytest
import json
from synapse.core.orchestrator import Orchestrator
from synapse.core.engine import AgentEngine
from synapse.llm.base import BaseLLMAdapter, LLMResponse

class MockOrchestratorLLM(BaseLLMAdapter):
    async def generate(self, messages, tools=None) -> LLMResponse:
        # If it's the first turn, call the sub-agent tool
        if messages[-1]["role"] == "user":
            return LLMResponse(
                content=None,
                tool_calls=[{
                    "id": "call_1",
                    "function": {
                        "name": "ask_researcher",
                        "arguments": '{"query": "find data"}'
                    }
                }]
            )
        # Second turn, return final answer based on tool result
        elif messages[-1]["role"] == "tool":
            return LLMResponse(content=f"Final Answer: {messages[-1]['content']}")
        return LLMResponse(content="Error")

class MockSubAgentLLM(BaseLLMAdapter):
    async def generate(self, messages, tools=None) -> LLMResponse:
        return LLMResponse(content="Data found: 42")

@pytest.mark.asyncio
async def test_orchestrator_delegation():
    from synapse.core.memory import Memory
    from synapse.core.event_bus import EventBus
    from synapse.tools.registry import ToolRegistry
    
    orch = Orchestrator(llm=MockOrchestratorLLM())
    
    sub_agent = AgentEngine(
        llm=MockSubAgentLLM(),
        memory=Memory(),
        event_bus=EventBus(),
        tool_registry=ToolRegistry()
    )
    
    orch.add_agent(
        name="researcher",
        description="Finds data.",
        agent=sub_agent
    )
    
    # Verify tool is registered
    assert "ask_researcher" in orch.tool_registry.tools
    
    result = await orch.process("Hey orchestrator, find data.")
    assert result == "Final Answer: Data found: 42"

@pytest.mark.asyncio
async def test_orchestrator_duplicate_agent():
    from synapse.core.memory import Memory
    from synapse.core.event_bus import EventBus
    from synapse.tools.registry import ToolRegistry
    
    orch = Orchestrator(llm=MockOrchestratorLLM())
    sub_agent = AgentEngine(
        llm=MockSubAgentLLM(),
        memory=Memory(),
        event_bus=EventBus(),
        tool_registry=ToolRegistry()
    )
    
    orch.add_agent("researcher", "desc", sub_agent)
    
    with pytest.raises(ValueError):
        orch.add_agent("researcher", "desc", sub_agent)
