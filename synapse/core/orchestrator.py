from typing import Dict, Any, Optional
from synapse.core.engine import AgentEngine
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.base import BaseLLMAdapter

class Orchestrator:
    """
    Manages multiple AgentEngines, exposing them to the manager agent as tools.
    """
    def __init__(
        self,
        llm: BaseLLMAdapter,
        memory: Optional[Memory] = None,
        event_bus: Optional[EventBus] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_iterations: int = 10
    ):
        self.memory = memory or Memory()
        self.event_bus = event_bus or EventBus()
        self.tool_registry = tool_registry or ToolRegistry()
        
        self.manager = AgentEngine(
            llm=llm,
            memory=self.memory,
            event_bus=self.event_bus,
            tool_registry=self.tool_registry,
            max_iterations=max_iterations
        )
        self.agents: Dict[str, AgentEngine] = {}

    def add_agent(self, name: str, description: str, agent: AgentEngine) -> None:
        """
        Adds a sub-agent to the orchestrator.
        This dynamically registers a tool in the manager's registry that routes tasks to the sub-agent.
        """
        if name in self.agents:
            raise ValueError(f"Agent with name '{name}' already exists.")
            
        self.agents[name] = agent
        
        # Create a dynamic function to act as the tool
        async def ask_agent(query: str) -> str:
            # Emit an event that we are delegating
            await self.event_bus.emit("on_agent_handoff", name, query)
            # Route the query to the sub-agent
            result = await agent.process(query, agentic_mode=True)
            return result
        
        # Override the __name__ and __doc__ so the registry parses it correctly
        ask_agent.__name__ = f"ask_{name}"
        ask_agent.__doc__ = description
        
        self.tool_registry.register(ask_agent)

    async def process(self, user_input: str) -> str:
        """
        Processes a user input using the manager agent.
        """
        return await self.manager.process(user_input, agentic_mode=True)
