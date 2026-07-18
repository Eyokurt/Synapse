import pytest
from synapse.core.persistent_memory import SQLiteMemory

@pytest.fixture
def memory():
    return SQLiteMemory(db_path=':memory:', session_id='test_session')

def test_add_and_get_messages(memory):
    msg1 = {"role": "user", "content": "Hello"}
    memory.add_message(msg1)
    
    msgs = memory.get_messages()
    assert len(msgs) == 1
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "Hello"

def test_deduplication(memory):
    msg1 = {"role": "user", "content": "Hello"}
    memory.add_message(msg1)
    memory.add_message(msg1) # Duplicate, should be ignored
    
    msgs = memory.get_messages()
    assert len(msgs) == 1

    msg2 = {"role": "user", "content": "Different"}
    memory.add_message(msg2)
    msgs = memory.get_messages()
    assert len(msgs) == 2

def test_tool_calls(memory):
    msg = {
        "role": "assistant",
        "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "test"}}]
    }
    memory.add_message(msg)
    msgs = memory.get_messages()
    assert len(msgs) == 1
    assert msgs[0]["tool_calls"] == [{"id": "call_1", "type": "function", "function": {"name": "test"}}]
    assert "content" not in msgs[0]

def test_clear(memory):
    memory.add_message({"role": "user", "content": "Hello"})
    memory.clear()
    assert len(memory.get_messages()) == 0

def test_delete_message(memory):
    id1 = memory.add_message({"role": "user", "content": "Message 1"})
    id2 = memory.add_message({"role": "user", "content": "Message 2"})
    
    assert id1 is not None
    assert id2 is not None
    
    memory.delete_message(id1)
    
    msgs = memory.get_messages()
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Message 2"
