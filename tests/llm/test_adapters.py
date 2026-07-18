import pytest
from synapse.llm.mock_adapter import MockAdapter

@pytest.mark.asyncio
async def test_mock_adapter():
    adapter = MockAdapter(mock_response="Mocked")
    response = await adapter.generate(messages=[{"role": "user", "content": "hello"}])
    assert response.content == "Mocked"
    assert response.tool_calls is None
