# System Architecture

Synapse is designed around three decoupled pillars:
1. **The LLM Layer:** Translates provider-specific APIs into a unified structure.
2. **The Audio Layer:** Manages native OS audio streams and local ML models for voice detection.
3. **The Core Orchestrator:** Manages state, executes tools, and loops the interaction.

## High-Level Flow (Voice Assistant Use Case)

1. **Listen:** `AudioStreamer` captures bytes from the microphone.
2. **Detect:** `SileroVAD` continuously analyzes 32ms chunks (using exact 64-sample overlap contexts).
3. **Buffer:** `VoiceLoop` accumulates chunks while speech is active and yields a complete buffer when silence is detected.
4. **Transcribe (Future):** STT model converts the audio buffer to text.
5. **Think:** `AgentEngine` receives the text, sends it to the `LLMAdapter`, and processes any requested tool calls.
6. **Speak (Future):** TTS model converts the agent's text response back to audio.
7. **Play:** `AudioPlayer` plays the resulting audio buffer natively through the OS speakers.

## Dependency Injection via SynapseConfig
All modules accept a `SynapseConfig` object. This prevents global state mutations and allows you to run multiple separate environments (e.g., an 8000Hz telephone simulation alongside a 48000Hz studio simulation) in the same Python process.

If no config is provided, modules default to `synapse.config.default_config`.
