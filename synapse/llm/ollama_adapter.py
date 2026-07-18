from synapse.llm.openai_adapter import OpenAIAdapter
from synapse.config import SynapseConfig, default_config
from typing import Optional

class OllamaAdapter(OpenAIAdapter):
    """
    Adapter for Local Ollama models.
    Leverages Ollama's OpenAI-compatible API endpoint.
    """
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, api_key: str = "ollama", config: Optional[SynapseConfig] = None):
        self.config = config or default_config
        actual_model = model or self.config.default_ollama_model
        actual_url = base_url or self.config.default_ollama_base_url
        super().__init__(model=actual_model, api_key=api_key, config=self.config)
        
        # Override the client with Ollama's local URL
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key, base_url=actual_url)
