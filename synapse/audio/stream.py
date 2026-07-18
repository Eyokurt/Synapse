import queue
import numpy as np

from synapse.config import SynapseConfig, default_config
from typing import Optional

class AudioStreamer:
    """
    Captures live audio from the microphone using PyAudio/SoundDevice.
    Requires sounddevice and numpy.
    """
    def __init__(self, sample_rate: Optional[int] = None, chunk_duration_ms: Optional[int] = None, config: Optional[SynapseConfig] = None):
        self.config = config or default_config
        self.sample_rate = sample_rate or self.config.audio_sample_rate
        self.chunk_duration_ms = chunk_duration_ms or self.config.audio_chunk_duration_ms
        # Calculate chunk size in frames
        self.chunk_size = int(self.sample_rate * self.chunk_duration_ms / 1000)
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

    def _audio_callback(self, indata, frames, time, status):
        """Called by sounddevice for each audio block."""
        if status:
            print(f"Audio status warning: {status}")
        # Convert audio to mono (channel 0) and copy it
        audio_data = indata[:, 0].copy()
        self.audio_queue.put(audio_data)

    def start(self):
        """Starts capturing audio from the default microphone."""
        self.stream = self.sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
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
