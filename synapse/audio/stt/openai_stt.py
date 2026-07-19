import io
import os
import numpy as np
import scipy.io.wavfile as wav
from typing import Optional
from .base import BaseSTTAdapter

class OpenAISTTAdapter(BaseSTTAdapter):
    """
    Speech-to-Text adapter using OpenAI's Whisper API.
    Requires `openai` package and OPENAI_API_KEY.
    """
    def __init__(self, model_name: str = "whisper-1", language: str = "tr", api_key: Optional[str] = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai package to use OpenAISTTAdapter: `pip install openai`")
            
        self.model_name = model_name
        self.language = language
        
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
            
        self.client = OpenAI(api_key=api_key)
        
    def _float32_to_int16(self, audio_data: np.ndarray) -> np.ndarray:
        return np.int16(audio_data * 32767)

    async def transcribe(self, audio_data: np.ndarray, sample_rate: int) -> str:
        # Convert to int16 for WAV saving
        audio_int16 = self._float32_to_int16(audio_data)
        
        wav_io = io.BytesIO()
        wav.write(wav_io, sample_rate, audio_int16)
        wav_io.seek(0)
        wav_io.name = "audio.wav"
        
        import asyncio
        loop = asyncio.get_event_loop()
        
        # Run synchronous OpenAI call in a thread pool to avoid blocking the event loop
        def _call_api():
            return self.client.audio.transcriptions.create(
                model=self.model_name,
                file=wav_io,
                language=self.language
            )
            
        transcription = await loop.run_in_executor(None, _call_api)
        return transcription.text
