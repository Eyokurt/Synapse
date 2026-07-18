import asyncio
import os
from synapse.core.engine import AgentEngine
from synapse.tools.registry import ToolRegistry

async def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable.")
        return

    registry = ToolRegistry()
    registry.register_builtins(["system", "web_search"])

    agent = AgentEngine(api_key=api_key, tool_registry=registry)
    
    prompt = "What time is it now, and what is the latest news about AI?"
    print(f"User: {prompt}")
    
    response = await agent.run(prompt)
    print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
