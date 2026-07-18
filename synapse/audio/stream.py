import queue
import numpy as np

from synapse.config import SynapseConfig, default_config
from synapse.audio.utils import resample_audio
from typing import Optional

class AudioStreamer:
    """
    Captures live audio from the microphone using PyAudio/SoundDevice.
    Requires sounddevice and numpy.
    Automatically handles hardware sample rate mismatches by resampling to config sample rate.
    """
    def __init__(self, sample_rate: Optional[int] = None, chunk_duration_ms: Optional[int] = None, config: Optional[SynapseConfig] = None):
        self.config = config or default_config
        self.target_sample_rate = sample_rate or self.config.audio_sample_rate
        self.chunk_duration_ms = chunk_duration_ms or self.config.audio_chunk_duration_ms
        
        self.audio_queue = queue.Queue()
        self.stream = None
        
        try:
            import sounddevice as sd
        except ImportError:
            raise ImportError(
                "sounddevice is required for AudioStreamer. "
                "Install it with `uv add centrumlib[audio]` or `pip install sounddevice numpy`"
            )
        self.sd = sd
        
        # Get native sample rate
        device_info = self.sd.query_devices(self.sd.default.device[0], 'input')
        self.native_sr = int(device_info['default_samplerate'])
        
        # Calculate expected exact length for VAD (e.g. 512 samples)
        self.target_chunk_size = int(self.target_sample_rate * self.chunk_duration_ms / 1000)
        # Calculate chunk size in native frames
        self.native_chunk_size = int(self.native_sr * self.chunk_duration_ms / 1000)

    def _audio_callback(self, indata, frames, time, status):
        """Called by sounddevice for each audio block."""
        if status:
            pass # Ignore minor underflows to prevent console spam
        
        audio_data = indata[:, 0].copy()
        
        # Resample to EXACT target chunk size (e.g. 512)
        if len(audio_data) != self.target_chunk_size:
            audio_data = resample_audio(audio_data, self.target_chunk_size)
            
        self.audio_queue.put(audio_data)

    def start(self):
        """Starts capturing audio from the default microphone."""
        self.stream = self.sd.InputStream(
            samplerate=self.native_sr,
            channels=1,
            blocksize=self.native_chunk_size,
            dtype=np.float32,
            callback=self._audio_callback
        )
        self.stream.start()

    def stop(self):
        """Stops capturing audio."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def get_chunk(self) -> np.ndarray:
        """
        Gets the next chunk of audio from the queue, blocking until available.
        Returns a 1D numpy array.
        """
        return self.audio_queue.get()
