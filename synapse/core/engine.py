import json
import logging
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.base import BaseLLMAdapter
from typing import Optional

from synapse.config import SynapseConfig, default_config

logger = logging.getLogger(__name__)

class AgentEngine:
    def __init__(
        self,
        llm: BaseLLMAdapter,
        memory: Memory,
        event_bus: EventBus,
        tool_registry: ToolRegistry,
        max_iterations: Optional[int] = None,
        config: Optional[SynapseConfig] = None
    ) -> None:
        self.config = config or default_config
        self.llm = llm
        self.memory = memory
        self.event_bus = event_bus
        self.tool_registry = tool_registry
        self.agentic_mode = False
        self.max_iterations = max_iterations or self.config.max_agentic_iterations

    async def process(self, user_input: str, agentic_mode: bool = False) -> str:
        self.agentic_mode = agentic_mode
        if self.agentic_mode:
            return await self._run_agentic_loop(user_input)

        self.memory.add_message("user", user_input)
        
        messages = self.memory.get_messages()
        response = await self.llm.generate(messages=messages)
        
        response_text = response.content or ""
        self.memory.add_message("assistant", response_text)
        
        await self.event_bus.emit("on_response", response_text)
        
        return response_text

    async def _run_agentic_loop(self, user_input: str) -> str:
        self.memory.add_message("user", user_input)
        
        for _ in range(self.max_iterations):
            messages = self.memory.get_messages()
            tools = self.tool_registry.get_schemas()
            
            response = await self.llm.generate(messages=messages, tools=tools)
            response_text = response.content or ""
            
            self.memory.add_message("assistant", response_text, tool_calls=response.tool_calls)
            
            if response_text:
                await self.event_bus.emit("on_response", response_text)
            
            if not response.tool_calls:
                return response_text
                
            for tool_call in response.tool_calls:
                tool_call_id = tool_call.get("id")
                func = tool_call.get("function", tool_call)
                name = func.get("name", "")
                args_str = func.get("arguments", "{}")
                
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    args = {}
                    
                try:
                    await self.event_bus.emit("on_tool_call", name, args)
                    result = await self.tool_registry.execute(name, **args)
                    result_str = str(result)
                except Exception as e:
                    result_str = f"Error: {str(e)}"
                    logger.error(f"Tool {name} failed: {e}")
                    
                self.memory.add_message("tool", result_str, tool_call_id=tool_call_id)
                
        raise RuntimeError(f"Max iterations ({self.max_iterations}) reached without completing the task.")
