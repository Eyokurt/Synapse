import pytest
from synapse.core.persistent_memory import SQLiteMemory

@pytest.fixture
def memory():
    return SQLiteMemory(db_path=':memory:', session_id='test_session')

def test_add_and_get_messages(memory):
    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi there")
    
    messages = memory.get_messages()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there"

def test_deduplication(memory):
    memory.add_message("user", "Hello")
    # Same exact message again
    memory.add_message("user", "Hello")
    
    # Should only have 1
    messages = memory.get_messages()
    assert len(messages) == 1

    # Different message should be added
    memory.add_message("user", "Hello 2")
    messages = memory.get_messages()
    assert len(messages) == 2

def test_tool_calls(memory):
    tool_calls = [{"id": "call_1", "type": "function", "function": {"name": "test"}}]
    memory.add_message("assistant", None, tool_calls=tool_calls)
    
    messages = memory.get_messages()
    assert len(messages) == 1
    assert messages[0]["tool_calls"] == tool_calls

def test_clear(memory):
    memory.add_message("user", "Hello")
    memory.clear()
    assert len(memory.get_messages()) == 0

def test_delete_message(memory):
    id1 = memory.add_message("user", "Message 1")
    id2 = memory.add_message("user", "Message 2")
    
    assert id1 is not None
    assert id2 is not None
    
    memory.delete_message(id1)
    
    msgs = memory.get_messages()
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Message 2"
