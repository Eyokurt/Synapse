from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.base import BaseLLMAdapter

class AgentEngine:
    def __init__(
        self,
        llm: BaseLLMAdapter,
        memory: Memory,
        event_bus: EventBus,
        tool_registry: ToolRegistry
    ) -> None:
        self.llm = llm
        self.memory = memory
        self.event_bus = event_bus
        self.tool_registry = tool_registry
        self.agentic_mode = False

    async def process(self, user_input: str) -> str:
        self.memory.add_message("user", user_input)
        
        messages = self.memory.get_messages()
        response = await self.llm.generate(messages=messages)
        
        response_text = response.content or ""
        self.memory.add_message("assistant", response_text)
        
        await self.event_bus.emit("on_response", response_text)
        
        return response_text
