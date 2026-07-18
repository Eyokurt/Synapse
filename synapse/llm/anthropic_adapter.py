import json
from typing import Any, Dict, List, Optional
from anthropic import AsyncAnthropic
from synapse.llm.base import BaseLLMAdapter, LLMResponse

class AnthropicAdapter(BaseLLMAdapter):
    """
    Adapter for Anthropic Claude models.
    Automatically maps OpenAI-style message and tool formats to Anthropic formats.
    """
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        system_prompt = ""
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt += msg.get("content", "") + "\n"
            elif msg["role"] == "user":
                anthropic_messages.append({"role": "user", "content": msg.get("content", "")})
            elif msg["role"] == "assistant":
                if msg.get("tool_calls"):
                    content = []
                    if msg.get("content"):
                        content.append({"type": "text", "text": msg["content"]})
                    for tc in msg["tool_calls"]:
                        args = tc["function"]["arguments"]
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except json.JSONDecodeError:
                                args = {}
                        content.append({
                            "type": "tool_use",
                            "id": tc["id"],
                            "name": tc["function"]["name"],
                            "input": args
                        })
                    anthropic_messages.append({"role": "assistant", "content": content})
                else:
                    anthropic_messages.append({"role": "assistant", "content": msg.get("content", "")})
            elif msg["role"] == "tool":
                anthropic_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.get("tool_call_id", ""),
                        "content": str(msg.get("content", ""))
                    }]
                })

        # Map tools
        anthropic_tools = []
        if tools:
            for t in tools:
                func = t.get("function", {})
                anthropic_tools.append({
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {"type": "object", "properties": {}})
                })

        kwargs = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": anthropic_messages
        }
        if system_prompt:
            kwargs["system"] = system_prompt.strip()
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools

        response = await self.client.messages.create(**kwargs)

        # Parse response back to LLMResponse
        text_content = None
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_content = block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input)
                    }
                })

        return LLMResponse(
            content=text_content,
            tool_calls=tool_calls if tool_calls else None
        )
