from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class LLMResponse(BaseModel):
    content: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]] = None

class BaseLLMAdapter(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        pass
