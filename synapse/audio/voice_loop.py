import sys
from typing import Optional, Callable
from synapse.config import SynapseConfig, default_config
from synapse.audio.vad import SileroVAD
from synapse.audio.stream import AudioStreamer

class VoiceLoop:
    """
    Orchestrates live microphone streaming and Voice Activity Detection (VAD).
    Triggers callbacks when speech starts and ends, abstracting away the chunk-level logic.
    """
    def __init__(self, config: Optional[SynapseConfig] = None):
        self.config = config or default_config
        
        self.vad = SileroVAD(config=self.config)
        self.streamer = AudioStreamer(config=self.config)
        
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        self.on_speech_ongoing: Optional[Callable] = None

    def start(self):
        """
        Starts the continuous blocking loop.
        Press Ctrl+C to interrupt.
        """
        # Calculate how many silence chunks equal the configured silence duration
        chunks_per_second = 1000 / self.config.audio_chunk_duration_ms
        silence_threshold_chunks = int((self.config.vad_silence_duration_ms / 1000) * chunks_per_second)
        
        self.streamer.start()
        
        is_talking = False
        silence_chunks = 0
        
        try:
            while True:
                chunk = self.streamer.get_chunk()
                has_voice = self.vad.is_speech(chunk)
                
                if has_voice:
                    if not is_talking:
                        is_talking = True
                        if self.on_speech_start:
                            self.on_speech_start()
                    else:
                        if self.on_speech_ongoing:
                            self.on_speech_ongoing()
                    silence_chunks = 0
                else:
                    if is_talking:
                        silence_chunks += 1
                        if silence_chunks >= silence_threshold_chunks:
                            is_talking = False
                            silence_chunks = 0
                            if self.on_speech_end:
                                self.on_speech_end()
        except KeyboardInterrupt:
            pass
        finally:
            self.streamer.stop()
