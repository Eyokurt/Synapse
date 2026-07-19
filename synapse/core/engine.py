import json
import logging
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.base import BaseLLMAdapter
from typing import Optional, Tuple
import numpy as np

try:
    from synapse.audio.stt.base import BaseSTTAdapter
    from synapse.audio.tts.base import BaseTTSAdapter
except ImportError:
    BaseSTTAdapter = None
    BaseTTSAdapter = None

from synapse.config import SynapseConfig, default_config

logger = logging.getLogger(__name__)

class AgentEngine:
    def __init__(
        self,
        llm: BaseLLMAdapter,
        memory: Memory,
        event_bus: EventBus,
        tool_registry: ToolRegistry,
        stt_adapter: Optional['BaseSTTAdapter'] = None,
        tts_adapter: Optional['BaseTTSAdapter'] = None,
        max_iterations: Optional[int] = None,
        config: Optional[SynapseConfig] = None
    ) -> None:
        self.config = config or default_config
        self.llm = llm
        self.memory = memory
        self.event_bus = event_bus
        self.tool_registry = tool_registry
        self.stt_adapter = stt_adapter
        self.tts_adapter = tts_adapter
        self.agentic_mode = False
        self.max_iterations = max_iterations or self.config.max_agentic_iterations

    async def process(self, user_input: str, agentic_mode: bool = False) -> str:
        self.agentic_mode = agentic_mode
        if self.agentic_mode:
            return await self._run_agentic_loop(user_input)

        self.memory.add_message("user", user_input)
        
        messages = self.memory.get_messages()
        response = await self.llm.generate(messages=messages)
        
        response_text = response.content or ""
        self.memory.add_message("assistant", response_text)
        
        await self.event_bus.emit("on_response", response_text)
        
        return response_text

    async def process_audio(self, audio_data: np.ndarray, sample_rate: int, agentic_mode: bool = False) -> Tuple[str, str, Optional[Tuple[int, np.ndarray]]]:
        """
        Takes raw audio data, transcribes it using STT, processes it with the LLM, 
        and optionally synthesizes the response using TTS.
        
        Returns:
            Tuple containing: (transcribed_user_text, ai_response_text, tts_audio_tuple)
        """
        if not self.stt_adapter:
            raise ValueError("STT adapter is not configured for this AgentEngine.")
            
        user_text = await self.stt_adapter.transcribe(audio_data, sample_rate)
        if not user_text.strip():
            return ("", "", None)
            
        ai_response = await self.process(user_text, agentic_mode=agentic_mode)
        
        tts_audio = None
        if self.tts_adapter and ai_response:
            tts_audio = await self.tts_adapter.synthesize(ai_response)
            
        return (user_text, ai_response, tts_audio)

    async def _run_agentic_loop(self, user_input: str) -> str:
        self.memory.add_message("user", user_input)
        
        for _ in range(self.max_iterations):
            messages = self.memory.get_messages()
            tools = self.tool_registry.get_schemas()
            
            response = await self.llm.generate(messages=messages, tools=tools)
            response_text = response.content or ""
            
            self.memory.add_message("assistant", response_text, tool_calls=response.tool_calls)
            
            if response_text:
                await self.event_bus.emit("on_response", response_text)
            
            if not response.tool_calls:
                return response_text
                
            for tool_call in response.tool_calls:
                tool_call_id = tool_call.get("id")
                func = tool_call.get("function", tool_call)
                name = func.get("name", "")
                args_str = func.get("arguments", "{}")
                
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    args = {}
                    
                try:
                    await self.event_bus.emit("on_tool_call", name, args)
                    result = await self.tool_registry.execute(name, **args)
                    result_str = str(result)
                except Exception as e:
                    result_str = f"Error: {str(e)}"
                    logger.error(f"Tool {name} failed: {e}")
                    
                self.memory.add_message("tool", result_str, tool_call_id=tool_call_id)
                
        raise RuntimeError(f"Max iterations ({self.max_iterations}) reached without completing the task.")
