import asyncio
from typing import Callable, Any, Dict, List

class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event: str, handler: Callable[..., Any]) -> None:
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(handler)

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        handlers = self._subscribers.get(event, [])
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(asyncio.create_task(handler(*args, **kwargs)))
            else:
                handler(*args, **kwargs)
        
        if tasks:
            await asyncio.gather(*tasks)
