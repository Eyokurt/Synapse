import os
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

from synapse.llm.base import BaseLLMAdapter, LLMResponse

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, model: str = "gpt-4o"):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        
        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                })

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls
        )
