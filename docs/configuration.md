# Configuration

Synapse uses a centralized dependency-injected dataclass for configuration. This avoids hidden global states and allows multiple completely isolated instances of the framework to run in the same process.

## The `SynapseConfig` Class

Located in `synapse/config.py`, this class holds all configurable parameters.

### Audio Parameters
- `audio_sample_rate`: (int) The target sample rate (default `16000`).
- `audio_chunk_duration_ms`: (int) The size of chunks evaluated by VAD (default `32`).
- `audio_silence_threshold`: (float) The probability threshold for VAD (default `0.5`).
- `audio_silence_duration_ms`: (int) Milliseconds of silence required before finalizing an audio capture buffer (default `1500`).

### Modifying the Config

You can pass a custom config to any component during initialization. If omitted, components fall back to a globally initialized `default_config`.

```python
from synapse.config import SynapseConfig
from synapse.audio.vad import SileroVAD

custom_config = SynapseConfig(
    audio_sample_rate=8000,
    audio_silence_duration_ms=2000
)

# Initializes VAD targeting 8000Hz telephone audio
vad = SileroVAD(config=custom_config)
```
