import pytest
from synapse.core.memory import Memory

def test_memory_add_message():
    mem = Memory()
    mem.add_message(role="user", content="Hello")
    messages = mem.get_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"

def test_memory_clear():
    mem = Memory()
    mem.add_message(role="user", content="Hello")
    mem.clear()
    assert len(mem.get_messages()) == 0

def test_memory_add_message_with_tools():
    mem = Memory()
    mem.add_message(
        role="assistant",
        content="",
        tool_calls=[{"id": "call_123", "type": "function", "function": {"name": "get_weather", "arguments": "{}"}}]
    )
    messages = mem.get_messages()
    assert len(messages) == 1
    assert messages[0]["tool_calls"] is not None
    assert messages[0]["tool_calls"][0]["id"] == "call_123"

def test_memory_tool_message():
    mem = Memory()
    mem.add_message(role="tool", content="Sunny", tool_call_id="call_123")
    messages = mem.get_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "tool"
    assert messages[0]["tool_call_id"] == "call_123"
