import os
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

from synapse.llm.base import BaseLLMAdapter, LLMResponse

from synapse.config import SynapseConfig, default_config

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, config: Optional[SynapseConfig] = None):
        self.config = config or default_config
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set and no api_key was provided")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model or self.config.default_openai_model

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        formatted_messages = []
        for msg in messages:
            formatted = {"role": msg["role"], "content": msg.get("content", "")}
            if "tool_calls" in msg and msg["tool_calls"]:
                formatted["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": tc["arguments"]
                        }
                    } for tc in msg["tool_calls"]
                ]
            if "tool_call_id" in msg:
                formatted["tool_call_id"] = msg["tool_call_id"]
            formatted_messages.append(formatted)

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": formatted_messages,
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
