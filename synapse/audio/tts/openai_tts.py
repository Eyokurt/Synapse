import io
import os
import numpy as np
import scipy.io.wavfile as wav
import warnings
from typing import Optional, Tuple
from .base import BaseTTSAdapter

class OpenAITTSAdapter(BaseTTSAdapter):
    """
    Text-to-Speech adapter using OpenAI's TTS API.
    Requires `openai` package and OPENAI_API_KEY.
    """
    def __init__(self, model_name: str = "tts-1", voice: str = "alloy", api_key: Optional[str] = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai package to use OpenAITTSAdapter: `pip install openai`")
            
        self.model_name = model_name
        self.voice = voice
        
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
            
        self.client = OpenAI(api_key=api_key)

    async def synthesize(self, text: str) -> Tuple[int, np.ndarray]:
        import asyncio
        loop = asyncio.get_event_loop()
        
        def _call_api():
            return self.client.audio.speech.create(
                model=self.model_name,
                voice=self.voice,
                input=text,
                response_format="wav"
            )
            
        tts_response = await loop.run_in_executor(None, _call_api)
        
        # Suppress SciPy warnings about EOF (OpenAI streams WAV without length headers)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=wav.WavFileWarning)
            out_wav_io = io.BytesIO(tts_response.content)
            out_sr, out_audio = wav.read(out_wav_io)
            
        if out_audio.dtype == np.int16:
            out_audio = out_audio.astype(np.float32) / 32768.0
            
        return out_sr, out_audio
