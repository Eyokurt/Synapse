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

    async def execute_tool(self, name: str, arguments: dict) -> Any:
        try:
            return await self.execute(name, **arguments)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"

    def get_schemas(self) -> List[Dict[str, Any]]:
        schemas: List[Dict[str, Any]] = []
        for name, func in self.tools.items():
            desc = self.tool_descriptions.get(name, "")
            sig = inspect.signature(func)
            properties = {}
            required = []
            for param_name, param in sig.parameters.items():
                param_type = "string"  # default
                if param.annotation is int: param_type = "integer"
                elif param.annotation is bool: param_type = "boolean"
                
                properties[param_name] = {"type": param_type}
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
                    
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": desc,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            })
        return schemas

def agent_tool(registry: ToolRegistry, description: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return registry.register(func, description)
    return decorator
