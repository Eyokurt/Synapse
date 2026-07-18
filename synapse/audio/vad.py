import os
import numpy as np

from synapse.config import SynapseConfig, default_config
from typing import Optional

class SileroVAD:
    """
    Voice Activity Detection using Silero VAD (ONNX).
    Requires onnxruntime and httpx to be installed.
    """
    def __init__(self, sample_rate: Optional[int] = None, threshold: Optional[float] = None, config: Optional[SynapseConfig] = None):
        self.config = config or default_config
        self.sample_rate = sample_rate or self.config.audio_sample_rate
        self.threshold = threshold if threshold is not None else self.config.vad_speech_threshold
        
        try:
            import onnxruntime
            import httpx
        except ImportError:
            raise ImportError(
                "onnxruntime and httpx are required for Silero VAD. "
                "Install them with `uv add centrumlib[audio]` or `pip install onnxruntime httpx`"
            )

        self.model_path = os.path.join(os.path.dirname(__file__), "silero_vad.onnx")
        self._download_model_if_needed(httpx)

        self.session = onnxruntime.InferenceSession(self.model_path)
        self.state = np.zeros((2, 1, 128), dtype=np.float32)
        # 0-D Scalar Tensor for sample rate (ONNX requires this exact shape, otherwise STFT paths fail silently)
        self.sr_tensor = np.array(self.sample_rate, dtype=np.int64)
        
        # Silero VAD v5 ONNX requires context buffer prepended to every frame
        # (64 samples for 16000Hz, 32 samples for 8000Hz)
        context_size = 64 if self.sample_rate == 16000 else 32
        self.context = np.zeros(context_size, dtype=np.float32)

    def _download_model_if_needed(self, httpx):
        if not os.path.exists(self.model_path):
            print("Downloading Silero VAD ONNX model (~1.8 MB)...")
            url = "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
            response = httpx.get(url, follow_redirects=True)
            with open(self.model_path, "wb") as f:
                f.write(response.content)

    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Calculates the probability of speech in a given raw audio chunk.
        audio_chunk should be a 1D numpy array of float32.
        """
        if audio_chunk.ndim > 1:
            audio_chunk = audio_chunk.reshape(-1)
            
        # 1. Prepend previous context to current chunk (e.g., 64 + 512 = 576 samples)
        model_input = np.concatenate((self.context, audio_chunk))
        
        # 2. Save the last `context_size` samples for the NEXT chunk
        self.context = audio_chunk[-len(self.context):].copy()

        inputs = {
            "input": np.expand_dims(model_input.astype(np.float32), axis=0),
            "sr": self.sr_tensor,
            "state": self.state
        }
        
        out, self.state = self.session.run(None, inputs)
        confidence = out[0][0]
        
        return float(confidence) >= self.threshold
