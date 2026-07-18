# Synapse

Synapse is a modular, AI-agnostic, and local-first Voice Assistant framework written in Python. It provides an extensible orchestrator to build multi-agent AI loops with completely local audio capture and processing.

## Features
- **LLM Agnostic:** Switch between OpenAI, Anthropic, or local Ollama models effortlessly.
- **Hardware-Aware Audio:** Built-in VAD (Voice Activity Detection) and audio capturing without relying on heavy frameworks. Uses pure ONNX and `sounddevice` to avoid CUDA bloat.
- **Multi-Agent Orchestration:** Define custom tools and multiple agents that can hand off tasks to one another.
- **Dependency Injected Configuration:** Centralized config (`SynapseConfig`) to easily override everything from system prompts to audio sample rates and silence thresholds.

## Installation

Ensure you have `uv` installed, then sync the dependencies:

```bash
uv sync
```

*(Alternatively, you can manually `pip install -r requirements.txt` or install dependencies: `pip install httpx numpy sounddevice onnxruntime python-dotenv`)*

## Running Examples

Synapse comes with several out-of-the-box examples to test its capabilities:

1. **Audio Echo Test (VAD & Playback):**
   *(Records your voice and plays it back to you using native sounddevice routing)*
   ```bash
   uv run python examples/echo_demo.py
   ```

2. **Voice Activity Detection (VAD) Test:**
   ```bash
   uv run python examples/vad_demo.py
   ```

3. **Multi-Agent Swarm (Terminal):**
   ```bash
   uv run python examples/multi_agent_demo.py
   ```

4. **Multiple LLM Adapters:**
   ```bash
   uv run python examples/multi_llm_demo.py
   ```

## Architecture

* `synapse/core/`: Contains the `AgentEngine` and `Agent` classes for step-by-step tool orchestration.
* `synapse/llm/`: Adapters for different LLM providers (`OpenAIAdapter`, `AnthropicAdapter`, `OllamaAdapter`).
* `synapse/audio/`: Voice loop (`VoiceLoop`), ONNX-based Silero VAD (`SileroVAD`), hardware-aware capturing (`AudioStreamer`), and native playback (`AudioPlayer`).

## License
MIT
