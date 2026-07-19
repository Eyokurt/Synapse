import numpy as np
from synapse.config import SynapseConfig, default_config
from synapse.audio.utils import resample_audio
from typing import Optional

class AudioPlayer:
    """
    Plays audio through the default speaker/output device using sounddevice.
    Automatically handles resampling from the application's audio sample rate to the hardware's native sample rate.
    """
    def __init__(self, config: Optional[SynapseConfig] = None):
        self.config = config or default_config
        
        try:
            import sounddevice as sd
        except ImportError:
            raise ImportError(
                "sounddevice is required for AudioPlayer. "
                "Install it with `uv add centrumlib[audio]` or `pip install sounddevice numpy`"
            )
        self.sd = sd
        
        # Get native sample rate for default output device
        # sd.default.device returns [input_device_id, output_device_id]
        device_info = self.sd.query_devices(self.sd.default.device[1], 'output')
        self.native_sr = int(device_info['default_samplerate'])

    def play(self, audio_data: np.ndarray, source_sr: Optional[int] = None, blocking: bool = True):
        """
        Plays a 1D numpy array of audio data.
        If source_sr is not provided, it assumes config.audio_sample_rate.
        If blocking is True, it waits until the audio finishes playing.
        """
        source_sr = source_sr or self.config.audio_sample_rate
        
        # Resample to native device rate if necessary
        if source_sr != self.native_sr:
            duration = len(audio_data) / source_sr
            target_len = int(duration * self.native_sr)
            audio_data = resample_audio(audio_data, target_len)
            
        self.sd.play(audio_data, samplerate=self.native_sr, blocking=blocking)
        
    def stop(self):
        """Stops any currently playing audio."""
        self.sd.stop()
