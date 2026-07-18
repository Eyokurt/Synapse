# Audio System & Hardware Interfacing

Synapse's Audio Layer is entirely local-first. It relies on `sounddevice` (a wrapper around PortAudio) to interface with Windows (WASAPI), macOS (CoreAudio), or Linux (ALSA/PulseAudio) directly.

## Components

### 1. `AudioStreamer`
Captures audio from the default microphone.
- Automatically handles dynamic block sizes.
- Converts everything to 32-bit floating point arrays (`float32` in `[-1.0, 1.0]`).

### 2. `SileroVAD`
Voice Activity Detection powered by ONNX Runtime. 
- **Strict Input Formatting:** Expects exactly 512 samples per chunk at 16000Hz (32ms of audio).
- **STFT Context Buffer:** Unlike simple PyTorch wrappers, direct ONNX inference requires maintaining a manual 64-sample history buffer. Synapse manages this internal `context` seamlessly, ensuring the neural network doesn't throw false positives or %0.1 silences due to truncated sine waves.

### 3. `VoiceLoop`
An orchestrator that runs the `AudioStreamer` in a background thread and evaluates chunks through `SileroVAD`.
- Configurable `silence_threshold` (e.g., 1.5 seconds of silence means the user stopped speaking).
- Yields complete, concatenated numpy arrays containing exactly one spoken phrase.

### 4. `AudioPlayer`
A simple interface to blast raw `numpy` arrays back to the default speaker natively. Supports blocking and non-blocking playback.

## Example: Raw Streaming
```python
from synapse.audio.stream import AudioStreamer
from synapse.audio.vad import SileroVAD

streamer = AudioStreamer()
vad = SileroVAD()

streamer.start()
try:
    while True:
        chunk = streamer.get_chunk()
        if vad.is_speech(chunk):
            print("Speech detected!")
finally:
    streamer.stop()
```
