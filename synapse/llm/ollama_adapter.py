from synapse.llm.openai_adapter import OpenAIAdapter

class OllamaAdapter(OpenAIAdapter):
    """
    Adapter for Local Ollama models.
    Leverages Ollama's OpenAI-compatible API endpoint.
    """
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434/v1", api_key: str = "ollama"):
        super().__init__(model=model, api_key=api_key)
        
        # Override the client with Ollama's local URL
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
