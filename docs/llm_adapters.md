# LLM Adapters

Synapse abstracts the complexities of different LLM providers using the `BaseLLMAdapter` interface.

## Supported Providers
- **OpenAI:** Requires the `openai` package and an `OPENAI_API_KEY`.
- **Anthropic:** Requires the `anthropic` package and an `ANTHROPIC_API_KEY`.
- **Ollama:** A fully local, free alternative. Requires an Ollama server running locally (usually on port 11434) and the `httpx` package.

## The `BaseLLMAdapter` Interface
Every adapter must implement two methods:
1. `generate_response(messages: List[Dict], tools: Optional[List[Callable]]) -> Dict`
2. `parse_tool_calls(response: Any) -> List[Dict]`

### Example: Using Ollama Locally
```python
from synapse.llm.ollama import OllamaAdapter

# Initializes the adapter pointing to the local Llama 3 model
llm = OllamaAdapter(model_name="llama3")

messages = [{"role": "user", "content": "What is the capital of France?"}]
response = llm.generate_response(messages)

print(response["content"])
```

### Implementing Custom Adapters
To add support for a new LLM provider (e.g., Google Gemini, Mistral API):
1. Inherit from `BaseLLMAdapter`.
2. Map Synapse's standard tool schema (`type`, `function`, `name`, `description`, `parameters`) into the specific schema your provider expects.
3. Map the provider's response back into Synapse's standardized output dictionary format:
   ```json
   {
       "content": "Assistant's text reply",
       "tool_calls": [
           {
               "name": "tool_name",
               "arguments": {"arg1": "value1"}
           }
       ]
   }
   ```
