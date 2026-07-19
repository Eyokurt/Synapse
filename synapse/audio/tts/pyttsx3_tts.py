import numpy as np
from typing import Tuple
from .base import BaseTTSAdapter
import io
import tempfile
import os
import scipy.io.wavfile as wav

class Pyttsx3TTSAdapter(BaseTTSAdapter):
    """
    Offline Text-to-Speech adapter using pyttsx3 (System Native TTS).
    Quality is robotic, but requires no model downloads.
    """
    def __init__(self, rate: int = 150):
        try:
            import pyttsx3
        except ImportError:
            raise ImportError("Please install pyttsx3: `pip install pyttsx3`")
            
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)

    async def synthesize(self, text: str) -> Tuple[int, np.ndarray]:
        import asyncio
        loop = asyncio.get_event_loop()
        
        def _generate():
            # pyttsx3 doesn't easily stream to numpy array, so we save to a temporary WAV file and read it
            temp_path = os.path.join(tempfile.gettempdir(), "pyttsx3_temp.wav")
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()
            
            sr, audio = wav.read(temp_path)
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            if audio.dtype == np.int16:
                audio = audio.astype(np.float32) / 32768.0
            
            return sr, audio
            
        sample_rate, samples = await loop.run_in_executor(None, _generate)
        return sample_rate, samples
