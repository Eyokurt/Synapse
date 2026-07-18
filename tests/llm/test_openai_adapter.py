import os
import unittest
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from synapse.llm.openai_adapter import OpenAIAdapter
from synapse.llm.base import LLMResponse

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        yield

def test_openai_adapter_missing_key():
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
            OpenAIAdapter()

@pytest.mark.asyncio
async def test_openai_adapter_generate(mock_env):
    with patch("synapse.llm.openai_adapter.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "test response"
        mock_message.tool_calls = None
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        adapter = OpenAIAdapter()
        response = await adapter.generate(messages=[{"role": "user", "content": "hi"}])

        assert isinstance(response, LLMResponse)
        assert response.content == "test response"
        assert response.tool_calls is None
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=[{"role": "user", "content": "hi"}],
        )

@pytest.mark.asyncio
async def test_openai_adapter_generate_with_tools(mock_env):
    with patch("synapse.llm.openai_adapter.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = None
        
        mock_tc = MagicMock()
        mock_tc.id = "call_123"
        mock_tc.function.name = "get_weather"
        mock_tc.function.arguments = '{"location": "London"}'
        mock_message.tool_calls = [mock_tc]
        
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        adapter = OpenAIAdapter()
        tools = [{"type": "function", "function": {"name": "get_weather"}}]
        response = await adapter.generate(
            messages=[{"role": "user", "content": "weather?"}],
            tools=tools
        )

        assert response.content is None
        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["id"] == "call_123"
        assert response.tool_calls[0]["name"] == "get_weather"
        assert response.tool_calls[0]["arguments"] == '{"location": "London"}'

        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=[{"role": "user", "content": "weather?"}],
            tools=tools
        )
