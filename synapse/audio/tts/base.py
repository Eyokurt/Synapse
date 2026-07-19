from typing import Protocol, Tuple
import numpy as np

class BaseTTSAdapter(Protocol):
    """
    Abstract interface for Text-to-Speech adapters.
    """
    async def synthesize(self, text: str) -> Tuple[int, np.ndarray]:
        """
        Synthesizes text into audio.
        
        Args:
            text: The text to synthesize.
            
        Returns:
            A tuple of (sample_rate, audio_data), where audio_data is a numpy array.
        """
        ...
