from typing import List, Dict, Any, Optional

class Memory:
    def __init__(self) -> None:
        self._messages: List[Dict[str, Any]] = []

    def add_message(
        self,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None
    ) -> None:
        message: Dict[str, Any] = {"role": role, "content": content}
        if tool_calls is not None:
            message["tool_calls"] = tool_calls
        if tool_call_id is not None:
            message["tool_call_id"] = tool_call_id
        self._messages.append(message)

    def get_messages(self) -> List[Dict[str, Any]]:
        return self._messages.copy()

    def clear(self) -> None:
        self._messages.clear()
