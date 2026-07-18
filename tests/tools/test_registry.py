import pytest
import asyncio
from typing import Any, Dict

from synapse.tools.registry import ToolRegistry, agent_tool

def test_registry_initialization() -> None:
    registry = ToolRegistry()
    assert len(registry.tools) == 0

def test_agent_tool_decorator_registers_function() -> None:
    registry = ToolRegistry()
    
    @agent_tool(registry=registry, description="Adds two numbers")
    def add(a: int, b: int) -> int:
        return a + b
        
    assert "add" in registry.tools
    assert registry.tools["add"].__name__ == "add"

@pytest.mark.asyncio
async def test_tool_execution() -> None:
    registry = ToolRegistry()
    
    @agent_tool(registry=registry)
    def multiply(a: int, b: int) -> int:
        return a * b
        
    @agent_tool(registry=registry)
    async def async_divide(a: int, b: int) -> float:
        return a / b
        
    res_sync = await registry.execute("multiply", a=2, b=3)
    assert res_sync == 6
    
    res_async = await registry.execute("async_divide", a=6, b=2)
    assert res_async == 3.0
    
def test_get_schemas() -> None:
    registry = ToolRegistry()
    
    @agent_tool(registry=registry, description="Calculate power")
    def power(base: int, exponent: int) -> int:
        return base ** exponent
        
    schemas = registry.get_schemas()
    assert len(schemas) == 1
    schema = schemas[0]
    assert schema["name"] == "power"
    assert schema["description"] == "Calculate power"

@pytest.mark.asyncio
async def test_execute_tool_error_handling() -> None:
    registry = ToolRegistry()
    
    @agent_tool(registry=registry)
    def crash_tool(a: int) -> int:
        raise RuntimeError("I crashed!")
        
    res_unregistered = await registry.execute_tool("missing", {"a": 1})
    assert isinstance(res_unregistered, str)
    assert "Error executing missing:" in res_unregistered
    
    res_crash = await registry.execute_tool("crash_tool", {"a": 1})
    assert isinstance(res_crash, str)
    assert "Error executing crash_tool: I crashed!" in res_crash
    
    @agent_tool(registry=registry)
    def ok_tool(a: int) -> int:
        return a * 2
        
    res_ok = await registry.execute_tool("ok_tool", {"a": 2})
    assert res_ok == 4
