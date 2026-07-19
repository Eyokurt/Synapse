from typing import Protocol
import numpy as np

class BaseSTTAdapter(Protocol):
    """
    Abstract interface for Speech-to-Text adapters.
    """
    async def transcribe(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Transcribes the given audio data into text.
        
        Args:
            audio_data: The 1D numpy array containing audio samples (float32).
            sample_rate: The sample rate of the audio data.
            
        Returns:
            The transcribed text.
        """
        ...
