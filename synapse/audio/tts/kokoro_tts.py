import numpy as np
from typing import Tuple
from .base import BaseTTSAdapter
import urllib.request
import os

class KokoroTTSAdapter(BaseTTSAdapter):
    """
    Offline Text-to-Speech adapter using Kokoro-ONNX.
    Provides very high quality local speech synthesis.
    Auto-downloads models on first run.
    """
    def __init__(self, voice: str = "af_bella", speed: float = 1.0):
        try:
            from kokoro_onnx import Kokoro
        except ImportError:
            raise ImportError("Please install kokoro-onnx and soundfile: `pip install kokoro-onnx soundfile`")
            
        self.voice = voice
        self.speed = speed
        
        # Ensure models are downloaded
        self._ensure_models_downloaded()
        
        # Initialize Kokoro
        self.kokoro = Kokoro(
            self.model_path,
            self.voices_path
        )

    def _ensure_models_downloaded(self):
        """Downloads the ONNX model and voices BIN if they don't exist in cache."""
        cache_dir = os.path.expanduser("~/.centrumlib_cache/kokoro")
        os.makedirs(cache_dir, exist_ok=True)
        
        self.model_path = os.path.join(cache_dir, "kokoro-v0_19.onnx")
        self.voices_path = os.path.join(cache_dir, "voices.bin")
        
        model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx"
        voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin"
        
        if not os.path.exists(self.model_path):
            print(f"[KokoroTTS] Downloading model (100MB+) to {self.model_path}...")
            urllib.request.urlretrieve(model_url, self.model_path)
            print("[KokoroTTS] Model downloaded successfully.")
            
        if not os.path.exists(self.voices_path):
            print(f"[KokoroTTS] Downloading voices to {self.voices_path}...")
            urllib.request.urlretrieve(voices_url, self.voices_path)
            print("[KokoroTTS] Voices downloaded successfully.")

    async def synthesize(self, text: str) -> Tuple[int, np.ndarray]:
        import asyncio
        loop = asyncio.get_event_loop()
        
        def _generate():
            # Split text into smaller chunks to avoid the 510 phoneme limit
            import re
            # Split by punctuation (., !, ?) keeping the punctuation
            raw_chunks = re.split(r'(?<=[.!?])\s+', text)
            chunks = []
            
            # Further split chunks that are absurdly long (e.g. JSON hallucinations)
            for c in raw_chunks:
                c = c.strip()
                if not c: continue
                # if still > 200 chars, chunk it forcefully
                while len(c) > 200:
                    chunks.append(c[:200])
                    c = c[200:]
                if c:
                    chunks.append(c)
                    
            if not chunks:
                chunks = [text[:200]]
                
            all_samples = []
            final_sample_rate = 24000
            
            for chunk in chunks:
                try:
                    samples, sample_rate = self.kokoro.create(
                        chunk,
                        voice=self.voice,
                        speed=self.speed,
                        lang="en-us" # Kokoro currently focuses heavily on English (en-us or en-gb)
                    )
                    all_samples.append(samples)
                    final_sample_rate = sample_rate
                except Exception as e:
                    print(f"[KokoroTTS] Chunk sentezlenirken hata oluştu: {e}")
                    
            if not all_samples:
                return final_sample_rate, np.zeros(0, dtype=np.float32)
                
            return final_sample_rate, np.concatenate(all_samples)
            
        sample_rate, samples = await loop.run_in_executor(None, _generate)
        return sample_rate, samples
