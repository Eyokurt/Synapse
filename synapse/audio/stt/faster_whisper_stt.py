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
        
        # Windows-specific CUDA DLL check & auto-downloader
        import sys
        if sys.platform == "win32" and device in ["auto", "cuda"]:
            import ctypes
            import os
            
            cuda_available = False
            try:
                ctypes.CDLL("cublas64_12.dll")
                cuda_available = True
            except OSError:
                pass
                
            if not cuda_available:
                print("\n[FasterWhisper] Uyarı: Sisteminizde NVIDIA CUDA kütüphaneleri bulunamadı.")
                print("[FasterWhisper] GPU hızlandırmasını aktif edebilmek için gerekli paketler otomatik indiriliyor...")
                print("[FasterWhisper] Bu işlem yaklaşık 500-700 MB sürebilir, lütfen sabırla bekleyin (sadece ilk seferde yapılır).")
                
                try:
                    import subprocess
                    import site
                    
                    # Install nvidia packages
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "nvidia-cublas-cu12", "nvidia-cudnn-cu12"])
                    
                    # Inject DLL directories
                    for sp in site.getsitepackages():
                        cublas_path = os.path.join(sp, "nvidia", "cublas", "bin")
                        cudnn_path = os.path.join(sp, "nvidia", "cudnn", "bin")
                        
                        for p in [cublas_path, cudnn_path]:
                            if os.path.exists(p):
                                os.environ["PATH"] = p + os.pathsep + os.environ["PATH"]
                                if hasattr(os, "add_dll_directory"):
                                    os.add_dll_directory(p)
                                    
                    # Verify
                    ctypes.CDLL("cublas64_12.dll")
                    cuda_available = True
                    print("[FasterWhisper] ✅ CUDA kütüphaneleri başarıyla indirildi ve sisteme entegre edildi!\n")
                except Exception as e:
                    print(f"\n[FasterWhisper] ❌ Otomatik indirme başarısız oldu: {e}")
                    
            if not cuda_available:
                print(f"[FasterWhisper] Çökmeyi engellemek için cihaz mecburen 'CPU' olarak ayarlanıyor...")
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
