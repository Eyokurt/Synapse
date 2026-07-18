import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from synapse.core.engine import AgentEngine
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.openai_adapter import OpenAIAdapter
from synapse.utils.logger import AgentLogger
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable.")
        return

    # Initialize Core
    memory = Memory()
    event_bus = EventBus()
    registry = ToolRegistry()
    logger = AgentLogger(event_bus)

    # Register builtin toolkits
    registry.register_builtins(["system", "web_search"])

    # Initialize LLM & Engine
    llm = OpenAIAdapter(model="gpt-4o-mini")
    agent = AgentEngine(
        llm=llm,
        memory=memory,
        event_bus=event_bus,
        tool_registry=registry,
        max_iterations=10
    )
    
    prompt = "What time is it now, and what is the latest news about AI? Search the web."
    print(f"User: {prompt}")
    
    response = await agent.process(prompt, agentic_mode=True)
    print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
