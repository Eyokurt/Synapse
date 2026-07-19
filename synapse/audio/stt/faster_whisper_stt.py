import numpy as np
from .base import BaseSTTAdapter

class FasterWhisperSTTAdapter(BaseSTTAdapter):
    """
    Offline Speech-to-Text adapter using faster-whisper.
    Requires `faster-whisper` package.
    Automatically downloads the specified model to the local huggingface cache.
    """
    def __init__(self, model_size: str = "base", device: str = "auto", compute_type: str = "int8", language: str = "tr"):
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError("Please install faster-whisper package: `pip install faster-whisper`")
            
        self.language = language
        
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as e:
            if device == "auto" or device == "cuda":
                print(f"[FasterWhisper] GPU başlatılamadı ({e}), CPU'ya düşülüyor...")
                self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            else:
                raise e

    async def transcribe(self, audio_data: np.ndarray, sample_rate: int) -> str:
        import asyncio
        loop = asyncio.get_event_loop()
        
        # faster-whisper expects float32 in range [-1, 1] which is exactly what we have,
        # but if it needs 16kHz, we should assure it's 16kHz. 
        # By default, VoiceLoop config uses 16000Hz, which is whisper's native rate.
        
        def _call_api():
            # We can pass the numpy array directly to transcribe()
            segments, info = self.model.transcribe(audio_data, language=self.language, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
            
        transcription = await loop.run_in_executor(None, _call_api)
        return transcription
