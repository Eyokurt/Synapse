import pytest
from synapse.llm.anthropic_adapter import AnthropicAdapter

def test_anthropic_init():
    adapter = AnthropicAdapter(api_key="test_key")
    assert adapter.model == "claude-3-haiku-20240307"
    assert adapter.client is not None

def test_ollama_init():
    from synapse.llm.ollama_adapter import OllamaAdapter
    adapter = OllamaAdapter(model="llama3", api_key="ollama")
    assert adapter.model == "llama3"
    assert adapter.client is not None
    # Base URL should point to local Ollama by default
    assert str(adapter.client.base_url) == "http://localhost:11434/v1/"
