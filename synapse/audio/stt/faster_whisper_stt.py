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
        self.model_size = model_size
        
        # Windows-specific CUDA DLL check to prevent ctranslate2 hard crashes and deadlocks
        import sys
        if sys.platform == "win32" and device in ["auto", "cuda"]:
            import ctypes
            cuda_available = False
            for dll_name in ["cublas64_12.dll", "cublas64_11.dll"]:
                try:
                    ctypes.CDLL(dll_name)
                    cuda_available = True
                    break
                except OSError:
                    pass
            
            if not cuda_available:
                print(f"[FasterWhisper] Uyarı: Sisteminizde gerekli CUDA kütüphaneleri bulunamadı (cublas64_12.dll). Çökmeyi engellemek için cihaz 'CPU' olarak ayarlanıyor...")
                device = "cpu"

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    async def transcribe(self, audio_data: np.ndarray, sample_rate: int) -> str:
        import asyncio
        loop = asyncio.get_event_loop()
        
        def _call_api():
            segments, info = self.model.transcribe(audio_data, language=self.language, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
            
        transcription = await loop.run_in_executor(None, _call_api)
        return transcription
