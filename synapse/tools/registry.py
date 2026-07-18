import asyncio
import inspect
from typing import Any, Callable, Dict, List, Optional

class ToolRegistry:
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.tool_descriptions: Dict[str, str] = {}

    def register(self, func: Callable[..., Any], description: Optional[str] = None) -> Callable[..., Any]:
        self.tools[func.__name__] = func
        self.tool_descriptions[func.__name__] = description or func.__doc__ or ""
        return func

    async def execute(self, name: str, **kwargs: Any) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        func = self.tools[name]
        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return await asyncio.to_thread(func, **kwargs)

    def get_schemas(self) -> List[Dict[str, Any]]:
        schemas: List[Dict[str, Any]] = []
        for name, desc in self.tool_descriptions.items():
            schemas.append({
                "name": name,
                "description": desc
            })
        return schemas

def agent_tool(registry: ToolRegistry, description: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return registry.register(func, description)
    return decorator
