import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv

load_dotenv()

from synapse.core.orchestrator import Orchestrator
from synapse.core.engine import AgentEngine
from synapse.tools.registry import ToolRegistry
from synapse.llm.openai_adapter import OpenAIAdapter

async def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable.")
        return

    llm = OpenAIAdapter(model="gpt-4o-mini")

    from synapse.core.memory import Memory
    from synapse.core.event_bus import EventBus

    # 1. Create Researcher Agent
    researcher_registry = ToolRegistry()
    researcher_registry.register_builtins(["web_search"])
    researcher = AgentEngine(
        llm=llm,
        memory=Memory(),
        event_bus=EventBus(),
        tool_registry=researcher_registry,
    )
    researcher.system_prompt = "You are a brilliant researcher. Use web_search to find factual data."

    # 2. Create Finance Agent
    finance_registry = ToolRegistry()
    finance_registry.register_builtins(["system"]) # For execute_python to do math
    finance = AgentEngine(
        llm=llm,
        memory=Memory(),
        event_bus=EventBus(),
        tool_registry=finance_registry,
    )
    finance.system_prompt = "You are a finance expert. Calculate taxes, projections, or do math using the python executor if needed."

    # 3. Create Orchestrator
    orchestrator = Orchestrator(llm=llm)
    orchestrator.manager.system_prompt = (
        "You are the Lead Orchestrator. You manage a Researcher and a Finance Expert. "
        "Coordinate their abilities to fulfill the user's request, synthesizing their answers into a final response."
    )

    # Add agents to the orchestrator (this automatically creates tools for them!)
    orchestrator.add_agent(
        name="researcher", 
        description="Delegates a query to the Researcher. Use this to find news, prices, or factual info online.", 
        agent=researcher
    )
    
    orchestrator.add_agent(
        name="finance_expert", 
        description="Delegates a query to the Finance Expert. Use this to calculate taxes, margins, or do financial math.", 
        agent=finance
    )

    prompt = "Find the latest stock price of Apple (AAPL) and calculate what a 20% capital gains tax would be on 100 shares."
    print(f"User: {prompt}\n")
    print("Orchestrator is thinking... (This might take a few seconds as agents communicate)\n")
    
    # Process
    response = await orchestrator.process(prompt)
    print(f"\nFinal Response from Orchestrator:\n{response}")

if __name__ == "__main__":
    asyncio.run(main())
