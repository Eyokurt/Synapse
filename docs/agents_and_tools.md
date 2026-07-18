# Agents and Tools

The `synapse.core` module handles the logic for defining agents and executing their tools.

## Defining Agents

An `Agent` encapsulates a system prompt, a designated LLM adapter, and a set of callable python functions (tools).

```python
from synapse.core import Agent
from synapse.llm.openai import OpenAIAdapter

llm = OpenAIAdapter(model_name="gpt-4o")

weather_agent = Agent(
    name="WeatherBot",
    role="You are a helpful weather assistant.",
    llm=llm,
    tools=[get_weather] # See below
)
```

## Creating Tools

Tools are standard Python functions. Synapse automatically parses their docstrings and type hints to generate the JSON Schema required by the underlying LLM.

```python
def get_weather(location: str) -> str:
    """
    Fetches the current weather for a given location.
    
    Args:
        location: The city and state, e.g. "San Francisco, CA"
    """
    return f"The weather in {location} is 72F and sunny."
```

## The Agent Engine

The `AgentEngine` is responsible for managing conversation history, executing tool calls safely, and passing state between agents in a multi-agent swarm.

```python
from synapse.core import AgentEngine

engine = AgentEngine()

# Start a conversation
response = engine.run(weather_agent, "What is the weather in Tokyo?")
print(response)
```

## Handoffs (Multi-Agent Swarm)

Agents can hand tasks off to other agents by returning an `Agent` instance from a tool. The `AgentEngine` will automatically switch the active context to the new agent.

```python
def transfer_to_support() -> Agent:
    """Transfers the user to a human support agent."""
    return support_agent
```
