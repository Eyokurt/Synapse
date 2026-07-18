import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from synapse.core.engine import AgentEngine
from synapse.tools.registry import ToolRegistry
from synapse.llm.openai_adapter import OpenAIAdapter
from synapse.llm.ollama_adapter import OllamaAdapter
from synapse.llm.anthropic_adapter import AnthropicAdapter

async def run_agent_with_llm(name: str, llm_adapter):
    print(f"\n--- Running with {name} ---")
    
    registry = ToolRegistry()
    registry.register_builtins(["system"])
    
    agent = AgentEngine(llm=llm_adapter, tool_registry=registry)
    
    try:
        response = await agent.process("Calculate 25 * 4 and tell me the result.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error during {name} run: {e}")

async def main():
    # 1. OpenAI (Standard)
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        await run_agent_with_llm("OpenAI (gpt-4o-mini)", OpenAIAdapter(model="gpt-4o-mini"))
    else:
        print("Skipping OpenAI run (OPENAI_API_KEY not set)")

    # 2. Ollama (Local)
    # Requires ollama to be running locally (`ollama run llama3`)
    # await run_agent_with_llm("Ollama (llama3 local)", OllamaAdapter(model="llama3"))

    # 3. Anthropic (Claude)
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        await run_agent_with_llm("Anthropic (claude-3-haiku)", AnthropicAdapter(api_key=anthropic_key))
    else:
        print("Skipping Anthropic run (ANTHROPIC_API_KEY not set)")

if __name__ == "__main__":
    asyncio.run(main())
