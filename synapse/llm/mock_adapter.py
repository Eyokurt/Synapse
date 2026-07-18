from typing import Any, Dict, List, Optional
from synapse.llm.base import BaseLLMAdapter, LLMResponse

class MockAdapter(BaseLLMAdapter):
    def __init__(self, mock_response: str):
        self.mock_response = mock_response

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        return LLMResponse(content=self.mock_response)
