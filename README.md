# Synapse Framework

Synapse is a local-first, modular Voice Assistant and Multi-Agent framework written in Python. It provides an orchestration layer to build autonomous AI loops, voice-activated agents, and multi-agent systems without relying on heavy external frameworks or cloud-based audio processing.

## Key Features

1. **LLM Agnosticism:** Interchangeable adapters for OpenAI, Anthropic, or local Ollama models. The framework unifies tool-calling and chat completions under a single interface.
2. **Local-First Audio Processing:** 
   - Uses ONNX-based Silero VAD v5 for Voice Activity Detection with exact STFT context overlap buffering.
   - Built on `sounddevice` (PortAudio) for hardware-aware audio capturing and playback. Does not require PyTorch or CUDA.
3. **Multi-Agent Orchestration:** Supports defining custom tools and multiple agents that can interact, use tools, and pass execution context to one another.
4. **Centralized Configuration:** Dependency-injected `SynapseConfig` dataclass for global parameters such as sample rates, VAD thresholds, and LLM settings.

## Installation

The recommended package manager is `uv`:

```bash
uv sync
```

To install manually via pip:
```bash
pip install httpx numpy sounddevice onnxruntime python-dotenv
```
*(Note: To use the OpenAI or Anthropic adapters, you must install `openai` or `anthropic` respectively.)*

## Documentation

Detailed technical documentation is available in the `docs/` directory:

- [System Architecture](docs/architecture.md)
- [LLM Adapters & Setup](docs/llm_adapters.md)
- [Audio Capture, VAD, and Playback](docs/audio_system.md)
- [Agents & Tools](docs/agents_and_tools.md)
- [Configuration Guide](docs/configuration.md)

## Examples

The `examples/` directory contains standalone scripts demonstrating core functionality:

1. **Audio Echo & VAD Demo:**
   Records microphone input using Silero VAD, detects silence, and plays the captured buffer back to the user natively.
   ```bash
   uv run python examples/echo_demo.py
   ```

2. **Multi-Agent Demo:**
   Demonstrates tool-calling and context passing between two distinct agents (e.g., a Researcher and a Developer) using the `AgentEngine`.
   ```bash
   uv run python examples/multi_agent_demo.py
   ```

3. **Multi-LLM Adapter Demo:**
   Executes inference across different LLM providers using the unified adapter interface.
   ```bash
   uv run python examples/multi_llm_demo.py
   ```

## Project Structure

```text
Centrumlib/
│
├── synapse/                # Core library
│   ├── core/               # Agent and Engine classes
│   ├── llm/                # Provider adapters (OpenAI, Anthropic, Ollama)
│   ├── audio/              # Streamer, Player, Silero VAD, VoiceLoop
│   └── config.py           # Global configuration dataclass
│
├── docs/                   # Technical documentation
│
└── examples/               # Demo scripts
```

## License
MIT License
