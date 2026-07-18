from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SynapseConfig:
    """
    Centralized Configuration Object for Synapse Framework.
    Allows easy overriding of default parameters across the entire framework.
    """
    
    # Core Engine
    max_agentic_iterations: int = 10
    
    # LLM Defaults
    default_openai_model: str = "gpt-4o-mini"
    default_anthropic_model: str = "claude-3-haiku-20240307"
    default_ollama_model: str = "llama3"
    default_ollama_base_url: str = "http://localhost:11434/v1"
    
    # Audio Processing Defaults
    audio_sample_rate: int = 16000
    audio_chunk_duration_ms: int = 32 # Silero VAD expects 512 samples at 16kHz (32ms)
    vad_speech_threshold: float = 0.5
    vad_silence_duration_ms: int = 1500  # Time in MS of silence before triggering end of speech

# Global default config instance
# Users can modify this singleton or instantiate their own.
default_config = SynapseConfig()
