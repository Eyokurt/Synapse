import asyncio
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from synapse.core.engine import AgentEngine
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.audio.voice_loop import VoiceLoop
from synapse.audio.player import AudioPlayer

# Use offline Ollama instead of OpenAI
from synapse.llm.ollama_adapter import OllamaAdapter

# Use Offline STT and TTS
from synapse.audio.stt import FasterWhisperSTTAdapter
from synapse.audio.tts import KokoroTTSAdapter

async def process_voice_async(audio_data: np.ndarray, loop: VoiceLoop, player: AudioPlayer, engine: AgentEngine):
    print("\n[🧠] Çevrimdışı işlem yapılıyor (STT -> LLM -> TTS)...")
    try:
        user_text, ai_response, tts_tuple = await engine.process_audio(
            audio_data=audio_data, 
            sample_rate=loop.config.audio_sample_rate,
            agentic_mode=True
        )
        
        if not user_text:
            print("[⚠️] Boş ses algılandı. Tekrar dinleniyor...")
            loop.streamer.start()
            return
            
        print(f"\n🗣️ Siz: {user_text}")
        print(f"🤖 Llama: {ai_response}")
        
        if tts_tuple:
            out_sr, out_audio = tts_tuple
            print("[🔊] Cevap çalınıyor...")
            player.play(out_audio, source_sr=out_sr, blocking=True)
            
    except Exception as e:
        print(f"\n[❌] Bir hata oluştu: {e}")

    print("\n[🎙️] Tekrar dinleniyor... (Kapatmak için Ctrl+C)")
    loop.streamer.start()

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("--- Synapse 100% Offline Assistant Demo ---")
    print("Lütfen Ollama uygulamasının arka planda çalıştığından emin olun (örn: `ollama run llama3.2`).")
    print("İlk çalıştırmada STT ve TTS modelleri cihazınıza indirilecektir. (Sabırlı olun!)")
    
    # 1. Setup LLM, STT, and TTS Adapters (Tümü Offline)
    print("\nModeller yükleniyor...")
    llm = OllamaAdapter(model="llama3.2")
    
    print("[STT] Faster-Whisper yükleniyor...")
    stt = FasterWhisperSTTAdapter(model_size="tiny", language="tr")
    
    print("[TTS] Kokoro-ONNX yükleniyor...")
    tts = KokoroTTSAdapter()
    
    # 2. Setup Tool Registry
    registry = ToolRegistry()
    registry.register_builtins(["system"]) # Sadece offline çalışabilen araçlar

    # 3. Create Agent Engine
    engine = AgentEngine(
        llm=llm,
        stt_adapter=stt,
        tts_adapter=tts,
        memory=Memory(),
        event_bus=EventBus(),
        tool_registry=registry
    )
    engine.system_prompt = (
        "Sen tamamen internetsiz (çevrimdışı) çalışan bir sesli asistansın. "
        "Yanıtlarını konuşulacağını bilerek kısa ve akıcı tut."
    )

    loop = VoiceLoop()
    player = AudioPlayer()

    def on_start():
        print("\n[🎙️] Konuşma Başladı! (Kaydediliyor...)")
        
    def on_ongoing():
        sys.stdout.write("• ")
        sys.stdout.flush()
        
    def on_end(audio_data: np.ndarray):
        duration = len(audio_data) / loop.config.audio_sample_rate
        print(f"\n[🔇] Konuşma Bitti. ({duration:.2f} saniye)")
        loop.streamer.stop()
        asyncio.run(process_voice_async(audio_data, loop, player, engine))
        
    loop.on_speech_start = on_start
    loop.on_speech_ongoing = on_ongoing
    loop.on_speech_end = on_end
    
    print("\n[🎙️] Sistem hazır! Mikrofon dinleniyor... (Durdurmak için Ctrl+C)")
    loop.start()

if __name__ == "__main__":
    main()
